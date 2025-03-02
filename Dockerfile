FROM python:3.9-slim

RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

COPY --chown=user ./requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY --chown=user . /app

# 如果您有静态文件和模板，确保它们被正确复制
# COPY --chown=user ./static /app/static
# COPY --chown=user ./templates /app/templates

# 使用gunicorn作为生产WSGI服务器
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "app:app"] 