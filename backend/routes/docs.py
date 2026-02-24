from __future__ import annotations

import os

from flask import Blueprint, Response, send_file

bp = Blueprint("docs", __name__)

OPENAPI_PATH = os.path.join(os.path.dirname(__file__), "..", "openapi.yaml")


@bp.get("/openapi.yaml")
def openapi_spec():
    return send_file(OPENAPI_PATH, mimetype="application/yaml")


@bp.get("/docs")
def swagger_ui():
    html = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <title>SaveYourMoney API Docs</title>
  <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css" />
  <style>
    body { margin: 0; background: #f7f7f7; }
    #swagger-ui { max-width: 1200px; margin: 0 auto; }
  </style>
</head>
<body>
  <div id="swagger-ui"></div>
  <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
  <script>
    window.onload = () => {
      window.ui = SwaggerUIBundle({
        url: '/openapi.yaml',
        dom_id: '#swagger-ui',
        presets: [SwaggerUIBundle.presets.apis],
        layout: 'BaseLayout'
      });
    };
  </script>
</body>
</html>
"""
    return Response(html, mimetype="text/html")
