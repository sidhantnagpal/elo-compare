#-*- coding:utf-8 -*-
'''
	python create_db.py

	store images present in static/compare/, in database having
	name format with underscore as separator and an extension
	examples
	* Apple_iPhone_6S.jpg
	* Google_Pixel.jpg
'''
import sys, os
from server import Player, db

def main():
	imgs = os.listdir('assets')

	db.drop_all()
	db.create_all()
	lst = []
	for img in imgs:
	    fullname = img.split('.')
	    if len(fullname) == 1 or \
	    		fullname[-1] not in ('jpg', 'jpeg', 'png', 'gif'):
	    	continue
	    name = fullname[0]
	    lst.append(name)
	    name = map(str, name.split('_'))
	    obj = Player(name=' '.join(name).decode('utf-8'), imgurl=img.decode('utf-8'))
	    db.session.add(obj)

	db.session.commit()
	print lst

main()