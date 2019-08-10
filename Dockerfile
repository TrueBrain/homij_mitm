FROM python:3.8-slim

WORKDIR /code

COPY requirements.txt /code/
COPY homij_mitm /code/homij_mitm

RUN pip --no-cache-dir install -r requirements.txt

# Validate that what was installed was what was expected
RUN pip freeze 2>/dev/null > requirements.installed \
        && diff -u --strip-trailing-cr requirements.txt requirements.installed 1>&2 \
        || ( echo "!! ERROR !! requirements.txt defined different packages or versions for installation" \
                && exit 1 ) 1>&2

ENTRYPOINT ["python", "-m", "homij_mitm"]
CMD []
