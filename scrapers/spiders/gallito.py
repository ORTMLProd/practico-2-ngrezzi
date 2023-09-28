import boto3
from typing import Iterator
from requests.utils import requote_uri
from scrapy.http.response.html import HtmlResponse
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapers.items import PropertyItem
import requests
import jsonlines

class GallitoSpider(CrawlSpider):
    name = "gallito"
    custom_settings = {
        "USER_AGENT": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        ),
    }
    start_urls = [
        "https://www.gallito.com.uy/inmuebles/casas",  # Cambia esta URL a la página que deseas raspar
    ]

    rules = (
        Rule(LinkExtractor(allow=(r"-\d{8}$")), callback="parse_property"),
    )

    def __init__(self, *args, **kwargs):
        super(GallitoSpider, self).__init__(*args, **kwargs)
        self.s3_bucket_name = "ml-en-produccion"
        self.s3_client = boto3.client("s3")
        self.property_data = []  # Lista para almacenar datos de propiedades

    def parse_property(self, response: HtmlResponse) -> Iterator[dict]:
        def get_with_css(query: str) -> str:
            return response.css(query).get(default="").strip()

        def extract_with_css(query: str) -> list[str]:
            return [
                line for elem in response.css(query).extract() if (line := elem.strip())
            ]

        # property details
        property_id = get_with_css("#HfCodigoAviso::attr('value')")
        img_urls = get_with_css("#HstrImg::attr('value')")
        img_urls = [img for img in img_urls.split(",") if img]
        possible_types = {
            "casa": "HOUSE",
            "apartamento": "APARTMENT",
        }

        # every property has this fixed list of details on gallito
        fixed_details = extract_with_css("div.iconoDatos + p::text")
        property_type = possible_types.get(fixed_details[0].lower(), "UNKNOWN")

        # Guardar imágenes comunes (JPEG, JPG, PNG)
        common_img_extensions = [".jpeg", ".jpg", ".png"]
        for img_url in img_urls:
            if any(img_url.lower().endswith(ext) for ext in common_img_extensions):
                property = {
                    "id": property_id,
                    "image_urls": [img_url],
                    "source": "gallito",
                    "url": requote_uri(response.request.url),
                    "link": requote_uri(response.request.url),
                    "property_type": property_type,
                }
                yield PropertyItem(**property)

                # Agregar la información a la lista property_data
                self.property_data.append(property)

    def closed(self, reason):
        # Cuando se cierra la araña, escribir los datos en el archivo y cargarlo en S3
        with jsonlines.open("properties_gallito.jl", mode="a") as writer:
            writer.write_all(self.property_data)

        # Subir el archivo JSONLines a S3
        with open("properties_gallito.jl", "rb") as jsonlines_file:
            self.s3_client.put_object(
                Bucket=self.s3_bucket_name,
                Key="properties_gallito.jl",
                Body=jsonlines_file,
            )