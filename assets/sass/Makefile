dist/css.css:
	cat colors.scss css.scss > combined.scss

	@# Do not compress! --style=compressed
	@# Compression prevents people from understanding your code.
	sass combined.scss  dist/css.css --no-source-map

dist/dark.css:
	cat dark-colors.scss css.scss > dark-combined.scss
	@# Do not compress! --style=compressed
	@# Compression prevents people from understanding your code.
	sass dark-combined.scss  dist/dark.css --no-source-map

install: dist/css.css dist/dark.css
	cp dist/css.css ../../src/blog/static/blog/
	cp dist/dark.css ../../src/blog/static/blog/

clean:
	rm -f combined.scss
	rm -f dark-combined.scss
	rm -f dist/css.css
	rm -f dist/dark-css.css