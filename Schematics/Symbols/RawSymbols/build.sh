
(
echo '(kicad_symbol_lib (version 20211014) (generator PHK115)'
rm -f F138_.txt
cat *.txt
echo ')'
) | sed '
s/ -0[.]00 / 0 /g
s/[.]\([1-9]\)0 /.\1 /g
' | python3 ../sexp.py > R1000.kicad_sym
