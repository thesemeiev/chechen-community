#!/bin/bash

# === НАСТРОЙКИ ===
PROJECT_NAME="my_flask_app"                     # Имя systemd-сервиса
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DOMAIN="сhechen-community.ru"                          # 🔁 ЗАМЕНИ на свой домен
PORT=8000

echo "📁 Папка проекта: $PROJECT_DIR"
echo "🌍 Домен: $DOMAIN"
echo "🔌 Gunicorn будет слушать порт $PORT"

# === УСТАНОВКА ЗАВИСИМОСТЕЙ ===
echo "📦 Устанавливаем зависимости..."
sudo apt update
sudo apt install python3 python3-pip python3-venv nginx certbot python3-certbot-nginx -y

# === ВИРТУАЛЬНОЕ ОКРУЖЕНИЕ ===
echo "🐍 Создаём виртуальное окружение..."
python3 -m venv "$PROJECT_DIR/venv"
source "$PROJECT_DIR/venv/bin/activate"
pip install --upgrade pip
pip install flask gunicorn

# === SYSTEMD СЛУЖБА ===
echo "🛠️ Создаём systemd-сервис..."
SERVICE_PATH="/etc/systemd/system/${PROJECT_NAME}.service"
sudo tee "$SERVICE_PATH" > /dev/null <<EOF
[Unit]
Description=Gunicorn instance to serve $PROJECT_NAME
After=network.target

[Service]
User=$USER
Group=www-data
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
ExecStart=$PROJECT_DIR/venv/bin/gunicorn -w 4 -b 127.0.0.1:$PORT app:app

[Install]
WantedBy=multi-user.target
EOF

# === ЗАПУСК СЛУЖБЫ ===
echo "🚀 Запускаем и активируем сервис..."
sudo systemctl daemon-reload
sudo systemctl start "$PROJECT_NAME"
sudo systemctl enable "$PROJECT_NAME"

# === НАСТРОЙКА NGINX ===
echo "🌐 Настраиваем Nginx для HTTP и редиректа..."
NGINX_PATH="/etc/nginx/sites-available/$PROJECT_NAME"
sudo tee "$NGINX_PATH" > /dev/null <<EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    location / {
        return 301 https://\$host\$request_uri;
    }
}
EOF

# Включаем сайт и перезапускаем Nginx
sudo ln -sf "$NGINX_PATH" /etc/nginx/sites-enabled/"$PROJECT_NAME"
sudo nginx -t && sudo systemctl reload nginx

# === HTTPS (Let's Encrypt) ===
echo "🔐 Получаем и настраиваем HTTPS-сертификат..."
sudo certbot --nginx -d "$DOMAIN" -d "www.$DOMAIN" --non-interactive --agree-tos -m thesemeiev@icloud.com

echo "✅ УСПЕХ! Сайт доступен по адресу: https://$DOMAIN"
