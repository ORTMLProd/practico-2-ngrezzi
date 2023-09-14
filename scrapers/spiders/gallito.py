import boto3
from typing import Iterator
from requests.utils import requote_uri
from scrapy.http.response.html import HtmlResponse
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapers.items import PropertyItem
import requests

class GallitoSpider(CrawlSpider):
    name = "gallito"
    custom_settings = {
        "USER_AGENT": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        ),
        "FEEDS": {
            "properties_gallito.jl": {"format": "jsonlines"},
        },
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
        property_type = possible_types[fixed_details[0].lower()]

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

                # Subir los datos a S3 (cambia la extensión según sea necesario)
                self.upload_to_s3(img_url, property_id)

    def upload_to_s3(self, url, filename):
        try:
            image_data = requests.get(url).content
            # Determina la extensión del archivo desde la URL
            file_extension = url.split(".")[-1].lower()
            if file_extension in ["jpeg", "jpg"]:
                s3_key = f"{filename}.jpg"
            elif file_extension == "png":
                s3_key = f"{filename}.png"
            else:
                # Extension no reconocida, puedes manejarlo según sea necesario
                s3_key = f"{filename}.unknown"

            self.s3_client.put_object(
                Bucket=self.s3_bucket_name,
                Key=s3_key,
                Body=image_data,
            )
            self.logger.info(f"Uploaded {s3_key} to S3 bucket {self.s3_bucket_name}")
        except Exception as e:
            self.logger.error(f"Failed to upload {s3_key} to S3: {str(e)}")
