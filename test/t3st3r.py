import commands
import re

for java_instance_properties in commands.getoutput('ps -ef').split('\n'):
	if re.search(r'java',java_instance_properties,re.I) and re.search(r'instance.properties',java_instance_properties) and not re.search(r'grep',java_instance_properties):
		return true
else
	return 