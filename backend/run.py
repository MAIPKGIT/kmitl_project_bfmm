# โค้ดเดิมของอั๋น
# from app import create_app

# app = create_app()

# if __name__ == "__main__":
#      app.run(host='0.0.0.0', port=5000, ssl_context=('certificate.crt', 'private.key'))

# โค้ดที่มายเอามาลองรันเครื่อง local
from app import create_app

app = create_app()

if __name__ == "__main__":
     app.run(debug=True)
