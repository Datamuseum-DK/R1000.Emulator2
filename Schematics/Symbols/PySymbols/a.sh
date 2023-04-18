
for i in *.py
do
	sed -i '' 's/Chipdesc[.]//' $i
	sed -i '' '/__main__/s/.*/def register():/' $i
	sed -i '' '
	/[.]main[(][)]/{
	s/^ */    yield /
	s/[.]main.*//
	}
	' $i
done
