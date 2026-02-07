.PHONY: install download list clean-cache gui help

# Variables
URL ?= 

help:
	@echo "Music Downloader - Comandos disponibles:"
	@echo ""
	@echo "  make install              Instala dependencias"
	@echo "  make gui                  Lanza la interfaz gráfica"
	@echo "  make download URL=<url>   Descarga música desde YouTube"
	@echo "  make list                 Lista canciones descargadas"
	@echo "  make clean-cache          Limpia el caché de descargas"
	@echo ""
	@echo "Ejemplos:"
	@echo "  make gui"
	@echo "  make download URL=\"https://youtube.com/watch?v=...\""
	@echo "  make download URL=\"https://youtube.com/playlist?list=...\""

install:
	uv sync

download:
ifndef URL
	@echo "Error: Debes especificar una URL"
	@echo "Uso: make download URL=<url>"
	@exit 1
endif
	uv run music-dl download --url "$(URL)"

list:
	@echo "Canciones descargadas:"
	@cat .downloaded.json 2>/dev/null | python3 -m json.tool || echo "No hay descargas registradas"

clean-cache:
	@rm -f .downloaded.json
	@echo "Caché limpiado"

gui:
	uv run music-dl gui
