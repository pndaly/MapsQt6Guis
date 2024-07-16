all: clean
	[ -f MapsQt6Guis.pdf ] && rm MapsQt6Guis.pdf || echo ""
	pdflatex MapsQt6Guis.tex
	pdflatex MapsQt6Guis.tex
	pdflatex MapsQt6Guis.tex
	make clean

clean:
	[ -f MapsQt6Guis.aux ] && rm MapsQt6Guis.aux || echo ""
	[ -f MapsQt6Guis.lof ] && rm MapsQt6Guis.lof || echo ""
	[ -f MapsQt6Guis.log ] && rm MapsQt6Guis.log || echo ""
	[ -f MapsQt6Guis.lot ] && rm MapsQt6Guis.lot || echo ""
	[ -f MapsQt6Guis.out ] && rm MapsQt6Guis.out || echo ""
	[ -f MapsQt6Guis.toc ] && rm MapsQt6Guis.toc || echo ""
