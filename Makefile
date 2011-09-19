# makefile to conveniently run tests against different versions of Plone
# please see https://github.com/witsch/plone-test-maker for more info

testmaker:
	curl -sL http://is.gd/plone_test_maker | make -sf-

