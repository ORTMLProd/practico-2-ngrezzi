[![Open in Codespaces](https://classroom.github.com/assets/launch-codespace-7f7980b617ed060a017424585567c406b6ee15c891e84e1186181d67ecf80aa0.svg)](https://classroom.github.com/open-in-codespaces?assignment_repo_id=11759554)

# Práctico 2 

- instalar: pip install awscli
- validar: aws --version
- agregar boto3

1. Loguearse a AWS academy e iniciar el entorno + Copiar AWS_ACCESS_KEY_ID ,  AWS_SECRET_ACCESS_KEY y  AWS_SESSION_TOKEN

2. Crear variables de entorno 

	- export AWS_ACCESS_KEY_ID= <YOUR-KEY>
	- export AWS_SECRET_ACCESS_KEY= <YOUR-KEY>
	- export AWS_SESSION_TOKEN= <YOUR-TOKEN>

	- echo $AWS_ACCESS_KEY_ID
	- echo $AWS_SECRET_ACCESS_KEY
	- echo $AWS_SESSION_TOKEN


	Con esto podemos validar que se setearon bien


3. Descomentar linea que escribe a [s3](https://aws.amazon.com/es/s3/) en settings.py
	
	IMAGES_STORE = "s3://ml-en-produccion"


4. Authenticarse con AWS ECR [(Elastic Container Registry)](https://aws.amazon.com/es/ecr/)

	aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com

aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 690157963428.dkr.ecr.us-east-1.amazonaws.com

5. Crear repositorio ECR 

	ml-en-prod-image-repository
	
5. buildead imagen 

	docker build -t scrapy .

6. taggear la imagen

	docker tag scrapy <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/ml-en-prod-image-repository:scrapy
	docker tag scrapy 690157963428.dkr.ecr.us-east-1.amazonaws.com/ml-en-prod-image-repository:scrapy

7. pushear imagen


	docker push <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/ml-en-prod-image-repository:scrapy
	docker push 690157963428.dkr.ecr.us-east-1.amazonaws.com/ml-en-prod-image-repository:scrapy


8. Entrar a la imagen con las claves

	docker run -it \
-e AWS_ACCESS_KEY_ID=<YOUR-KEY> \
-e AWS_SECRET_ACCESS_KEY=<YOUR-SECRET-KEY> \
-e AWS_SESSION_TOKEN=<YOUR-TOKEN> \
scrapy


docker run -it \
-e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
-e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
-e AWS_SESSION_TOKEN=$AWS_SESSION_TOKEN \
scrapy
	scrapy crawl gallito



# Recap: Práctico 1

En esta parte del práctico vamos a retomar los temas ya vistos en clase para construir un web scraper que extrae imágenes de propiedades del [Gallito](gallito.com.uy/).

Vamos a entrar en mayor profundidad en dependencias de python, web scraping, docker, y aws.

## Manejo de dependencias en Python
Usamos [`pip-tools`](https://pip-tools.readthedocs.io/en/latest/) para manejar las dependencias de Python. 
## Scrapy

Usamos [Scrapy](https://docs.scrapy.org/en/latest/) para construir la spider que va a recorrer el sitio del Gallito para extraer los datos de las propiedades.

Dentro de la documentación de Scrapy, les será útil revisar las entradas sobre:
* instalación
* [spiders](https://docs.scrapy.org/en/latest/topics/spiders.html), en especial la [CrawlSpider](https://docs.scrapy.org/en/latest/topics/spiders.html#crawlspider) y sus [Rules](https://docs.scrapy.org/en/latest/topics/spiders.html#crawling-rules)
* [link extractors](https://docs.scrapy.org/en/latest/topics/link-extractors.html)
* callbacks
* CSS [selectors](https://docs.scrapy.org/en/latest/topics/selectors.html)
* [Item Pipeline](https://docs.scrapy.org/en/latest/topics/item-pipeline.html), por ejemplo para descargar archivos o imágenes con una [MediaPipeline](https://docs.scrapy.org/en/latest/topics/media-pipeline.html) como la ImagesPipeline.

## Git

Llegado este práctico ya van a estar familiarizados con [git](https://git-scm.com/docs), [Github](https://github.com/), y sus comandos principales: init, add, commit, push, pull, status.

## Docker

Llegado este práctico ya van a estar familiarizados con el [Dockerfile](https://docs.docker.com/engine/reference/builder/), y los comandos docker [build](https://docs.docker.com/engine/reference/commandline/build/), [run](https://docs.docker.com/engine/reference/commandline/run/) y [push](https://docs.docker.com/engine/reference/commandline/push/). 
