dist/css.css:
	@# Do not compress! --style=compressed
	@# Compression prevents people from understanding your code.
	sass css.scss dist/css.css --no-source-map

install: dist/css.css
	cp dist/css.css ../../src/blog/static/blog/

clean:
	rm -f dist/css.css