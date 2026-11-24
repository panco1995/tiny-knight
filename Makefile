PYTHON ?= python3
APP := TinyKnight
DIST := dist
BUILD_DIR := build/$(APP)
APP_FILE := $(DIST)/$(APP).pyxapp
HTML_FILE := $(DIST)/$(APP).html

.PHONY: help run app web dist play serve exe clean distclean

help:
	@echo "Tiny Knight 构建命令"
	@echo ""
	@echo "  make run        从源码运行游戏"
	@echo "  make app        生成 $(APP_FILE)"
	@echo "  make web        生成网页版 $(HTML_FILE)"
	@echo "  make dist       同时生成 pyxapp 和网页版"
	@echo "  make play       运行已打包的 pyxapp"
	@echo "  make serve      启动本地服务器预览网页版 (端口 8000)"
	@echo "  make exe        生成当前系统的可执行文件 (需 PyInstaller)"
	@echo "  make clean      清理临时文件"
	@echo "  make distclean  清理临时文件和 dist/"
	@echo ""
	@echo "Windows 用户可直接运行 build_windows.bat。"

run:
	$(PYTHON) main.py

app: $(APP_FILE)

$(APP_FILE): main.py art.py
	rm -rf $(BUILD_DIR)
	mkdir -p $(BUILD_DIR) $(DIST)
	cp main.py art.py $(BUILD_DIR)/
	$(PYTHON) -m pyxel package $(BUILD_DIR) $(BUILD_DIR)/main.py
	mv $(APP).pyxapp $(DIST)/
	rm -rf $(BUILD_DIR)

web: $(HTML_FILE)

$(HTML_FILE): $(APP_FILE)
	$(PYTHON) -m pyxel app2html $(APP_FILE)
	mv -f $(APP).html $(DIST)/

dist: app web

play: $(APP_FILE)
	$(PYTHON) -m pyxel play $(APP_FILE)

serve: web
	@echo "Serving $(DIST) at http://localhost:8000/$(APP).html"
	$(PYTHON) -m http.server 8000 --directory $(DIST)

exe: $(APP_FILE)
	@$(PYTHON) -m PyInstaller --version >/dev/null 2>&1 || { \
		echo "PyInstaller is required: $(PYTHON) -m pip install pyinstaller"; \
		exit 1; \
	}
	$(PYTHON) -m pyxel app2exe $(APP_FILE)
	rm -rf $(DIST)/$(APP) $(DIST)/$(APP).app
	@if [ -d $(APP) ]; then mv $(APP) $(DIST)/; fi
	@if [ -d $(APP).app ]; then mv $(APP).app $(DIST)/; fi
	@echo "Done: see $(DIST)/"

clean:
	rm -rf build __pycache__ *.spec $(APP) $(APP).app

distclean: clean
	rm -rf $(DIST)
