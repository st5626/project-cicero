FROM python:3.8

WORKDIR /app

RUN apt-get install imagemagick

RUN pip install moviepy boto3

COPY . .

RUN sed -i '/<policy domain="path" rights="none" pattern="@\*"/d' /etc/ImageMagick-6/policy.xml

RUN convert -list font

CMD ["python3", "smash.py"]

