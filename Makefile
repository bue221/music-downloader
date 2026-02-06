.PHONY: install download list clean-cache help

# Variables
PLATFORM ?= youtube
URL ?= 

help:
	@echo "Music Downloader - Comandos disponibles:"
	@echo ""
	@echo "  make install              Instala dependencias"
	@echo "  make download PLATFORM=youtube|spotify URL=<url>"
	@echo "                            Descarga música desde la plataforma especificada"
	@echo "  make list                 Lista canciones descargadas"
	@echo "  make clean-cache          Limpia el caché de descargas"
	@echo ""
	@echo "Ejemplos:"
	@echo "  make download PLATFORM=youtube URL=\"https://youtube.com/watch?v=...\""
	@echo "  make download PLATFORM=spotify URL=\"https://open.spotify.com/playlist/...\""

install:
	uv sync

download:
ifndef URL
	@echo "Error: Debes especificar una URL"
	@echo "Uso: make download PLATFORM=$(PLATFORM) URL=<url>"
	@exit 1
endif
	uv run music-dl download --platform $(PLATFORM) --url "$(URL)"

list:
	@echo "Canciones descargadas:"
	@cat .downloaded.json 2>/dev/null | python3 -m json.tool || echo "No hay descargas registradas"

clean-cache:
	@rm -f .downloaded.json
	@echo "Caché limpiado"
