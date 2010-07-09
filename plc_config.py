#!/usr/bin/python
#
# Merge PlanetLab Central (PLC) configuration files into a variety of
# output formats. These files represent the global configuration for a
# PLC installation.
#
# Mark Huang <mlhuang@cs.princeton.edu>
# Copyright (C) 2006 The Trustees of Princeton University
#
# $Id$
#

import codecs
import os
import re
import sys
import textwrap
import time
import traceback
import types
import xml.dom.minidom
from xml.parsers.expat import ExpatError
from StringIO import StringIO
from optparse import OptionParser

class ConfigurationException(Exception): pass

class PLCConfiguration:
    """
    Configuration file store. Optionally instantiate with a file path
    or object:

    plc = PLCConfiguration()
    plc = PLCConfiguration(fileobj)
    plc = PLCConfiguration("/etc/planetlab/plc_config.xml")

    You may load() additional files later, which will be merged into
    the current configuration:

    plc.load("/etc/planetlab/local.xml")

    You may also save() the configuration. If a file path or object is
    not specified, the configuration will be written to the file path
    or object that was first loaded.
    
    plc.save()
    plc.save("/etc/planetlab/plc_config.xml")
    """

    def __init__(self, file = None):
        impl = xml.dom.minidom.getDOMImplementation()
        self._dom = impl.createDocument(None, "configuration", None)
        self._variables = {}
        self._packages = {}
        self._files = []

        if file is not None:
            self.load(file)


    def _get_text(self, node):
        """
        Get the text of a text node.
        """

        if node.firstChild and \
           node.firstChild.nodeType == node.TEXT_NODE:
            if node.firstChild.data is None:
                # Interpret simple presence of node as "", not NULL
                return ""
            else:
                return node.firstChild.data

        return None


    def _get_text_of_child(self, parent, name):
        """
        Get the text of a (direct) child text node.
        """

        for node in parent.childNodes:
            if node.nodeType == node.ELEMENT_NODE and \
               node.tagName == name:
                return self._get_text(node)

        return None


    def _set_text(self, node, data):
        """
        Set the text of a text node.
        """

        if node.firstChild and \
           node.firstChild.nodeType == node.TEXT_NODE:
            if data is None:
                node.removeChild(node.firstChild)
            else:
                node.firstChild.data = data
        elif data is not None:
            text = TrimText()
            text.data = data
            node.appendChild(text)


    def _set_text_of_child(self, parent, name, data):
        """
        Set the text of a (direct) child text node.
        """

        for node in parent.childNodes:
            if node.nodeType == node.ELEMENT_NODE and \
               node.tagName == name:
                self._set_text(node, data)
                return

        child = TrimTextElement(name)
        self._set_text(child, data)
        parent.appendChild(child)


    def _category_element_to_dict(self, category_element):
        """
        Turn a <category> element into a dictionary of its attributes
        and child text nodes.
        """

        category = {}
        category['id'] = category_element.getAttribute('id').lower()
        for node in category_element.childNodes:
            if node.nodeType == node.ELEMENT_NODE and \
               node.tagName in ['name', 'description']:
                category[node.tagName] = self._get_text_of_child(category_element, node.tagName)
        category['element'] = category_element

        return category


    def _variable_element_to_dict(self, variable_element):
        """
        Turn a <variable> element into a dictionary of its attributes
        and child text nodes.
        """

        variable = {}
        variable['id'] = variable_element.getAttribute('id').lower()
        if variable_element.hasAttribute('type'):
            variable['type'] = variable_element.getAttribute('type')
        for node in variable_element.childNodes:
            if node.nodeType == node.ELEMENT_NODE and \
               node.tagName in ['name', 'value', 'description']:
                variable[node.tagName] = self._get_text_of_child(variable_element, node.tagName)
        variable['element'] = variable_element

        return variable


    def _group_element_to_dict(self, group_element):
        """
        Turn a <group> element into a dictionary of its attributes
        and child text nodes.
        """

        group = {}
        for node in group_element.childNodes:
            if node.nodeType == node.ELEMENT_NODE and \
               node.tagName in ['id', 'name', 'default', 'description', 'uservisible']:
                group[node.tagName] = self._get_text_of_child(group_element, node.tagName)
        group['element'] = group_element

        return group


    def _packagereq_element_to_dict(self, packagereq_element):
        """
        Turns a <packagereq> element into a dictionary of its attributes
        and child text nodes.
        """

        package = {}
        if packagereq_element.hasAttribute('type'):
            package['type'] = packagereq_element.getAttribute('type')
        package['name'] = self._get_text(packagereq_element)
        package['element'] = packagereq_element

        return package


    def load(self, file = "/etc/planetlab/plc_config.xml"):
        """
        Merge file into configuration store.
        """

        try:
            dom = xml.dom.minidom.parse(file)
        except ExpatError, e:
            raise ConfigurationException, e

        if type(file) in types.StringTypes:
            self._files.append(os.path.abspath(file))

        # Parse <variables> section
        for variables_element in dom.getElementsByTagName('variables'):
            for category_element in variables_element.getElementsByTagName('category'):
                category = self._category_element_to_dict(category_element)
                self.set(category, None)

                for variablelist_element in category_element.getElementsByTagName('variablelist'):
                    for variable_element in variablelist_element.getElementsByTagName('variable'):
                        variable = self._variable_element_to_dict(variable_element)
                        self.set(category, variable)

        # Parse <comps> section
        for comps_element in dom.getElementsByTagName('comps'):
            for group_element in comps_element.getElementsByTagName('group'):
                group = self._group_element_to_dict(group_element)
                self.add_package(group, None)

                for packagereq_element in group_element.getElementsByTagName('packagereq'):
                    package = self._packagereq_element_to_dict(packagereq_element)
                    self.add_package(group, package)


    def save(self, file = None):
        """
        Write configuration store to file.
        """

        if file is None:
            if self._files:
                file = self._files[0]
            else:
                file = "/etc/planetlab/plc_config.xml"

        if type(file) in types.StringTypes:
            fileobj = open(file, 'w')
        else:
            fileobj = file

        fileobj.seek(0)
        fileobj.write(self.output_xml())
        fileobj.truncate()

        fileobj.close()

    def verify(self, default, read, verify_variables={}):
        """ Confirm that the existing configuration is consistent
            according to the checks below.

            It looks for filled-in values in the order of, local object (self),
            followed by cread (read values), and finally default values.

        Arguments: 

            default configuration
            site configuration
            list of category/variable tuples to validate in these configurations

        Returns:

            dict of values for the category/variables passed in
            If an exception is found, ConfigurationException is raised.

        """

        validated_variables = {}
        for category_id, variable_id in verify_variables.iteritems():
            category_id = category_id.lower()
            variable_id = variable_id.lower()
            variable_value = None
            sources = (self, read, default)
            for source in sources:
                (category_value, variable_value) = source.get(category_id,variable_id)
                if variable_value <> None:
                    entry = validated_variables.get(category_id,[])
                    entry.append(variable_value['value'])
                    validated_variables["%s_%s"%(category_id.upper(),variable_id.upper())]=entry
                    break
            if variable_value == None:
                raise ConfigurationException("Cannot find %s_%s)" % \
                                             (category_id.upper(),
                                              variable_id.upper()))
        return validated_variables

    def get(self, category_id, variable_id):
        """
        Get the specified variable in the specified category.

        Arguments:

        category_id = unique category identifier (e.g., 'plc_www')
        variable_id = unique variable identifier (e.g., 'port')

        Returns:

        variable = { 'id': "variable_identifier",
                     'type': "variable_type",
                     'value': "variable_value",
                     'name': "Variable name",
                     'description': "Variable description" }
        """

        if self._variables.has_key(category_id.lower()):
            (category, variables) = self._variables[category_id]
            if variables.has_key(variable_id.lower()):
                variable = variables[variable_id]
            else:
                variable = None
        else:
            category = None
            variable = None

        return (category, variable)


    def delete(self, category_id, variable_id):
        """
        Delete the specified variable from the specified category. If
        variable_id is None, deletes all variables from the specified
        category as well as the category itself.

        Arguments:

        category_id = unique category identifier (e.g., 'plc_www')
        variable_id = unique variable identifier (e.g., 'port')
        """

        if self._variables.has_key(category_id.lower()):
            (category, variables) = self._variables[category_id]
            if variable_id is None:
                category['element'].parentNode.removeChild(category['element'])
                del self._variables[category_id]
            elif variables.has_key(variable_id.lower()):
                variable = variables[variable_id]
                variable['element'].parentNode.removeChild(variable['element'])
                del variables[variable_id]


    def set(self, category, variable):
        """
        Add and/or update the specified variable. The 'id' fields are
        mandatory. If a field is not specified and the category and/or
        variable already exists, the field will not be updated. If
        'variable' is None, only adds and/or updates the specified
        category.

        Arguments:

        category = { 'id': "category_identifier",
                     'name': "Category name",
                     'description': "Category description" }

        variable = { 'id': "variable_identifier",
                     'type': "variable_type",
                     'value': "variable_value",
                     'name': "Variable name",
                     'description': "Variable description" }
        """

        if not category.has_key('id') or type(category['id']) not in types.StringTypes:
            return
        
        category_id = category['id'].lower()

        if self._variables.has_key(category_id):
            # Existing category
            (old_category, variables) = self._variables[category_id]

            # Merge category attributes
            for tag in ['name', 'description']:
                if category.has_key(tag):
                    old_category[tag] = category[tag]
                    self._set_text_of_child(old_category['element'], tag, category[tag])

            category_element = old_category['element']
        else:
            # Merge into DOM
            category_element = self._dom.createElement('category')
            category_element.setAttribute('id', category_id)
            for tag in ['name', 'description']:
                if category.has_key(tag):
                    self._set_text_of_child(category_element, tag, category[tag])

            if self._dom.documentElement.getElementsByTagName('variables'):
                variables_element = self._dom.documentElement.getElementsByTagName('variables')[0]
            else:
                variables_element = self._dom.createElement('variables')
                self._dom.documentElement.appendChild(variables_element)
            variables_element.appendChild(category_element)

            # Cache it
            category['element'] = category_element
            variables = {}
            self._variables[category_id] = (category, variables)

        if variable is None or not variable.has_key('id') or type(variable['id']) not in types.StringTypes:
            return

        variable_id = variable['id'].lower()

        if variables.has_key(variable_id):
            # Existing variable
            old_variable = variables[variable_id]

            # Merge variable attributes
            for attribute in ['type']:
                if variable.has_key(attribute):
                    old_variable[attribute] = variable[attribute]
                    old_variable['element'].setAttribute(attribute, variable[attribute])
            for tag in ['name', 'value', 'description']:
                if variable.has_key(tag):
                    old_variable[tag] = variable[tag]
                    self._set_text_of_child(old_variable['element'], tag, variable[tag])
        else:
            # Merge into DOM
            variable_element = self._dom.createElement('variable')
            variable_element.setAttribute('id', variable_id)
            for attribute in ['type']:
                if variable.has_key(attribute):
                    variable_element.setAttribute(attribute, variable[attribute])
            for tag in ['name', 'value', 'description']:
                if variable.has_key(tag):
                    self._set_text_of_child(variable_element, tag, variable[tag])
                
            if category_element.getElementsByTagName('variablelist'):
                variablelist_element = category_element.getElementsByTagName('variablelist')[0]
            else:
                variablelist_element = self._dom.createElement('variablelist')
                category_element.appendChild(variablelist_element)
            variablelist_element.appendChild(variable_element)

            # Cache it
            variable['element'] = variable_element
            variables[variable_id] = variable


    def locate_varname (self, varname):
        """
        Locates category and variable from a variable's (shell) name

        Returns:
        (variable, category) when found
        (None, None) otherwise
        """
        
        for (category_id, (category, variables)) in self._variables.iteritems():
            for variable in variables.values():
                (id, name, value, comments) = self._sanitize_variable(category_id, variable)
                if (id == varname):
                    return (category,variable)
        return (None,None)

    def get_package(self, group_id, package_name):
        """
        Get the specified package in the specified package group.

        Arguments:

        group_id - unique group id (e.g., 'plc')
        package_name - unique package name (e.g., 'postgresql')

        Returns:

        package = { 'name': "package_name",
                    'type': "mandatory|optional" }
        """

        if self._packages.has_key(group_id.lower()):
            (group, packages) = self._packages[group_id]
            if packages.has_key(package_name):
                package = packages[package_name]
            else:
                package = None
        else:
            group = None
            package = None

        return (group, package)


    def delete_package(self, group_id, package_name):
        """
        Deletes the specified variable from the specified category. If
        variable_id is None, deletes all variables from the specified
        category as well as the category itself.

        Arguments:

        group_id - unique group id (e.g., 'plc')
        package_name - unique package name (e.g., 'postgresql')
        """

        if self._packages.has_key(group_id):
            (group, packages) = self._packages[group_id]
            if package_name is None:
                group['element'].parentNode.removeChild(group['element'])
                del self._packages[group_id]
            elif packages.has_key(package_name.lower()):
                package = packages[package_name]
                package['element'].parentNode.removeChild(package['element'])
                del packages[package_name]


    def add_package(self, group, package):
        """
        Add and/or update the specified package. The 'id' and 'name'
        fields are mandatory. If a field is not specified and the
        package or group already exists, the field will not be
        updated. If package is None, only adds/or updates the
        specified group.

        Arguments:

        group = { 'id': "group_identifier",
                  'name': "Group name",
                  'default': "true|false",
                  'description': "Group description",
                  'uservisible': "true|false" }

        package = { 'name': "package_name",
                    'type': "mandatory|optional" }
        """

        if not group.has_key('id'):
            return

        group_id = group['id']

        if self._packages.has_key(group_id):
            # Existing group
            (old_group, packages) = self._packages[group_id]

            # Merge group attributes
            for tag in ['id', 'name', 'default', 'description', 'uservisible']:
                if group.has_key(tag):
                    old_group[tag] = group[tag]
                    self._set_text_of_child(old_group['element'], tag, group[tag])

            group_element = old_group['element']
        else:
            # Merge into DOM
            group_element = self._dom.createElement('group')
            for tag in ['id', 'name', 'default', 'description', 'uservisible']:
                if group.has_key(tag):
                    self._set_text_of_child(group_element, tag, group[tag])

            if self._dom.documentElement.getElementsByTagName('comps'):
                comps_element = self._dom.documentElement.getElementsByTagName('comps')[0]
            else:
                comps_element = self._dom.createElement('comps')
                self._dom.documentElement.appendChild(comps_element)
            comps_element.appendChild(group_element)

            # Cache it
            group['element'] = group_element
            packages = {}
            self._packages[group_id] = (group, packages)

        if package is None or not package.has_key('name'):
            return

        package_name = package['name']
        if packages.has_key(package_name):
            # Existing package
            old_package = packages[package_name]

            # Merge variable attributes
            for attribute in ['type']:
                if package.has_key(attribute):
                    old_package[attribute] = package[attribute]
                    old_package['element'].setAttribute(attribute, package[attribute])
        else:
            # Merge into DOM
            packagereq_element = TrimTextElement('packagereq')
            self._set_text(packagereq_element, package_name)
            for attribute in ['type']:
                if package.has_key(attribute):
                    packagereq_element.setAttribute(attribute, package[attribute])
                
            if group_element.getElementsByTagName('packagelist'):
                packagelist_element = group_element.getElementsByTagName('packagelist')[0]
            else:
                packagelist_element = self._dom.createElement('packagelist')
                group_element.appendChild(packagelist_element)
            packagelist_element.appendChild(packagereq_element)

            # Cache it
            package['element'] = packagereq_element
            packages[package_name] = package


    def variables(self):
        """
        Return all variables.

        Returns:

        variables = { 'category_id': (category, variablelist) }

        category = { 'id': "category_identifier",
                     'name': "Category name",
                     'description': "Category description" }

        variablelist = { 'variable_id': variable }

        variable = { 'id': "variable_identifier",
                     'type': "variable_type",
                     'value': "variable_value",
                     'name': "Variable name",
                     'description': "Variable description" }
        """

        return self._variables


    def packages(self):
        """
        Return all packages.

        Returns:

        packages = { 'group_id': (group, packagelist) }

        group = { 'id': "group_identifier",
                  'name': "Group name",
                  'default': "true|false",
                  'description': "Group description",
                  'uservisible': "true|false" }

        packagelist = { 'package_name': package }

        package = { 'name': "package_name",
                    'type': "mandatory|optional" }
        """

        return self._packages


    def _sanitize_variable(self, category_id, variable):
        assert variable.has_key('id')
        # Prepend variable name with category label
        id = category_id + "_" + variable['id']
        # And uppercase it
        id = id.upper()

        if variable.has_key('type'):
            type = variable['type']
        else:
            type = None

        if variable.has_key('name'):
            name = variable['name']
        else:
            name = None

        if variable.has_key('value') and variable['value'] is not None:
            value = variable['value']
            if type == "int" or type == "double":
                # bash, Python, and PHP do not require that numbers be quoted
                pass
            elif type == "boolean":
                # bash, Python, and PHP can all agree on 0 and 1
                if value == "true":
                    value = "1"
                else:
                    value = "0"
            else:
                # bash, Python, and PHP all support strong single quoting
                value = "'" + value.replace("'", "\\'") + "'"
        else:
            value = None

        if variable.has_key('description') and variable['description'] is not None:
            description = variable['description']
            # Collapse consecutive whitespace
            description = re.sub(r'\s+', ' ', description)
            # Wrap comments at 70 columns
            wrapper = textwrap.TextWrapper()
            comments = wrapper.wrap(description)
        else:
            comments = None

        return (id, name, value, comments)


    def _header(self):
        header = """
DO NOT EDIT. This file was automatically generated at
%s from:

%s
""" % (time.asctime(), os.linesep.join(self._files))

        # Get rid of the surrounding newlines
        return header.strip().split(os.linesep)


    def output_shell(self, show_comments = True, encoding = "utf-8"):
        """
        Return variables as a shell script.
        """

        buf = codecs.lookup(encoding)[3](StringIO())
        buf.writelines(["# " + line + os.linesep for line in self._header()])

        for (category_id, (category, variables)) in self._variables.iteritems():
            for variable in variables.values():
                (id, name, value, comments) = self._sanitize_variable(category_id, variable)
                if show_comments:
                    buf.write(os.linesep)
                    if name is not None:
                        buf.write("# " + name + os.linesep)
                    if comments is not None:
                        buf.writelines(["# " + line + os.linesep for line in comments])
                # bash does not have the concept of NULL
                if value is not None:
                    buf.write(id + "=" + value + os.linesep)

        return buf.getvalue()


    def output_php(self, encoding = "utf-8"):
        """
        Return variables as a PHP script.
        """

        buf = codecs.lookup(encoding)[3](StringIO())
        buf.write("<?php" + os.linesep)
        buf.writelines(["// " + line + os.linesep for line in self._header()])

        for (category_id, (category, variables)) in self._variables.iteritems():
            for variable in variables.values():
                (id, name, value, comments) = self._sanitize_variable(category_id, variable)
                buf.write(os.linesep)
                if name is not None:
                    buf.write("// " + name + os.linesep)
                if comments is not None:
                    buf.writelines(["// " + line + os.linesep for line in comments])
                if value is None:
                    value = 'NULL'
                buf.write("define('%s', %s);" % (id, value) + os.linesep)

        buf.write("?>" + os.linesep)

        return buf.getvalue()


    def output_xml(self, encoding = "utf-8"):
        """
        Return variables in original XML format.
        """

        buf = codecs.lookup(encoding)[3](StringIO())
        self._dom.writexml(buf, addindent = "  ", indent = "", newl = "\n", encoding = encoding)

        return buf.getvalue()


    def output_variables(self, encoding = "utf-8"):
        """
        Return list of all variable names.
        """

        buf = codecs.lookup(encoding)[3](StringIO())

        for (category_id, (category, variables)) in self._variables.iteritems():
            for variable in variables.values():
                (id, name, value, comments) = self._sanitize_variable(category_id, variable)
                buf.write(id + os.linesep)

        return buf.getvalue()


    def output_packages(self, encoding = "utf-8"):
        """
        Return list of all packages.
        """

        buf = codecs.lookup(encoding)[3](StringIO())

        for (group, packages) in self._packages.values():
            buf.write(os.linesep.join(packages.keys()))

        if buf.tell():
            buf.write(os.linesep)

        return buf.getvalue()


    def output_groups(self, encoding = "utf-8"):
        """
        Return list of all package group names.
        """

        buf = codecs.lookup(encoding)[3](StringIO())

        for (group, packages) in self._packages.values():
            buf.write(group['name'] + os.linesep)

        return buf.getvalue()


    def output_comps(self, encoding = "utf-8"):
        """
        Return <comps> section of configuration.
        """

        if self._dom is None or \
           not self._dom.getElementsByTagName("comps"):
            return
        comps = self._dom.getElementsByTagName("comps")[0]

        impl = xml.dom.minidom.getDOMImplementation()
        doc = impl.createDocument(None, "comps", None)

        buf = codecs.lookup(encoding)[3](StringIO())

        # Pop it off the DOM temporarily
        parent = comps.parentNode
        parent.removeChild(comps)

        doc.replaceChild(comps, doc.documentElement)
        doc.writexml(buf, encoding = encoding)

        # Put it back
        parent.appendChild(comps)

        return buf.getvalue()

    def validate_type(self, variable_type, value):

        # ideally we should use the "validate_*" methods in PLCAPI or
        # even declare some checks along with the default
        # configuration (using RELAX NG?) but this shall work for now.
        def ip_validator(val):
            import socket
            try:
                socket.inet_aton(val)
                return True
            except: return False

        def email_validator(val):
            return re.match('\A[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9._\-]+\.[a-zA-Z]+\Z', val)

        def boolean_validator (val):
            return val in ['true', 'false']

        validators = {
            'email' : email_validator,
            'ip': ip_validator,
            'boolean': boolean_validator,
            }

        # validate it if not a know type.
        validator = validators.get(variable_type, lambda x: True)
        return validator(value)



# xml.dom.minidom.Text.writexml adds surrounding whitespace to textual
# data when pretty-printing. Override this behavior.
class TrimText(xml.dom.minidom.Text):
    def writexml(self, writer, indent="", addindent="", newl=""):
        xml.dom.minidom.Text.writexml(self, writer, "", "", "")


class TrimTextElement(xml.dom.minidom.Element):
    def writexml(self, writer, indent="", addindent="", newl=""):
        writer.write(indent)
        xml.dom.minidom.Element.writexml(self, writer, "", "", "")
        writer.write(newl)


####################
# GLOBAL VARIABLES
#
release_id = "$Id$"
release_rev = "$Revision$"
release_url = "$URL$"

g_configuration=None
usual_variables=None
config_dir=None
service=None

def noop_validator(validated_variables):
    pass


# historically we could also configure the devel pkg....
def init_configuration ():
    global g_configuration
    global usual_variables, config_dir, service

    usual_variables=g_configuration["usual_variables"]
    config_dir=g_configuration["config_dir"]
    service=g_configuration["service"]

    global def_default_config, def_site_config, def_consolidated_config
    def_default_config= "%s/default_config.xml" % config_dir
    def_site_config = "%s/configs/site.xml" % config_dir
    def_consolidated_config = "%s/%s_config.xml" % (config_dir, service)

    global mainloop_usage
    mainloop_usage= """Available commands:
 Uppercase versions give variables comments, when available
 u/U\t\t\tEdit usual variables
 w\t\t\tWrite
 r\t\t\tRestart %(service)s service
 R\t\t\tReload %(service)s service (rebuild config files for sh, python....)
 q\t\t\tQuit (without saving)
 h/?\t\t\tThis help
---
 l/L [<cat>|<var>]\tShow Locally modified variables/values
 s/S [<cat>|<var>]\tShow variables/values (all, in category, single)
 e/E [<cat>|<var>]\tEdit variables (all, in category, single)
---
 c\t\t\tList categories
 v/V [<cat>|<var>]\tList Variables (all, in category, single)
---
Typical usage involves: u, [l,] w, r, q
""" % globals()

def usage ():
    command_usage="%prog [options] [default-xml [site-xml [consolidated-xml]]]"
    init_configuration ()
    command_usage +="""
\t default-xml defaults to %s
\t site-xml defaults to %s
\t consolidated-xml defaults to %s""" % (def_default_config,def_site_config, def_consolidated_config)
    return command_usage

####################
variable_usage= """Edit Commands :
#\tShow variable comments
.\tStops prompting, return to mainloop
/\tCleans any site-defined value, reverts to default
=\tShows default value
>\tSkips to next category
?\tThis help
"""

####################
def get_value (config,  category_id, variable_id):
    (category, variable) = config.get (category_id, variable_id)
    return variable['value']

def get_type (config, category_id, variable_id):
    (category, variable) = config.get (category_id, variable_id)
    return variable['type']

def get_current_value (cread, cwrite, category_id, variable_id):
    # the value stored in cwrite, if present, is the one we want
    try:
        result=get_value (cwrite,category_id,variable_id)
    except:
        result=get_value (cread,category_id,variable_id)
    return result

# refrain from using plc_config's _sanitize 
def get_varname (config,  category_id, variable_id):
    (category, variable) = config.get (category_id, variable_id)
    return (category_id+"_"+variable['id']).upper()

# could not avoid using _sanitize here..
def get_name_comments (config, cid, vid):
    try:
        (category, variable) = config.get (cid, vid)
        (id, name, value, comments) = config._sanitize_variable (cid,variable)
        return (name,comments)
    except:
        return (None,[])

def print_name_comments (config, cid, vid):
    (name,comments)=get_name_comments(config,cid,vid)
    if name:
        print "### %s" % name
    if comments:
        for line in comments:
            print "# %s" % line
    else:
        print "!!! No comment associated to %s_%s" % (cid,vid)

####################
def list_categories (config):
    result=[]
    for (category_id, (category, variables)) in config.variables().iteritems():
        result += [category_id]
    return result

def print_categories (config):
    print "Known categories"
    for cid in list_categories(config):
        print "%s" % (cid.upper())

####################
def list_category (config, cid):
    result=[]
    for (category_id, (category, variables)) in config.variables().iteritems():
        if (cid == category_id):
            for variable in variables.values():
                result += ["%s_%s" %(cid,variable['id'])]
    return result
    
def print_category (config, cid, show_comments=True):
    cid=cid.lower()
    CID=cid.upper()
    vids=list_category(config,cid)
    if (len(vids) == 0):
        print "%s : no such category"%CID
    else:
        print "Category %s contains" %(CID)
        for vid in vids:
            print vid.upper()

####################
def consolidate (default_config, site_config, consolidated_config):
    global service
    try:
        conso = PLCConfiguration (default_config)
        conso.load (site_config)
        conso.save (consolidated_config)
    except Exception, inst:
        print "Could not consolidate, %s" % (str(inst))
        return
    print ("Merged\n\t%s\nand\t%s\ninto\t%s"%(default_config,site_config,
                                              consolidated_config))

def reload_service ():
    global service
    os.system("set -x ; service %s reload" % service)
        
####################
def restart_service ():
    global service
    print ("==================== Stopping %s" % service)
    os.system("service %s stop" % service)
    print ("==================== Starting %s" % service)
    os.system("service %s start" % service)

####################
def prompt_variable (cdef, cread, cwrite, category, variable,
                     show_comments, support_next=False):

    assert category.has_key('id')
    assert variable.has_key('id')

    category_id = category ['id']
    variable_id = variable['id']

    while True:
        default_value = get_value(cdef,category_id,variable_id)
        variable_type = get_type(cdef,category_id,variable_id)
        current_value = get_current_value(cread,cwrite,category_id, variable_id)
        varname = get_varname (cread,category_id, variable_id)
        
        if show_comments :
            print_name_comments (cdef, category_id, variable_id)
        prompt = "== %s : [%s] " % (varname,current_value)
        try:
            answer = raw_input(prompt).strip()
        except EOFError :
            raise Exception ('BailOut')
        except KeyboardInterrupt:
            print "\n"
            raise Exception ('BailOut')

        # no change
        if (answer == "") or (answer == current_value):
            return None
        elif (answer == "."):
            raise Exception ('BailOut')
        elif (answer == "#"):
            print_name_comments(cread,category_id,variable_id)
        elif (answer == "?"):
            print variable_usage.strip()
        elif (answer == "="):
            print ("%s defaults to %s" %(varname,default_value))
        # revert to default : remove from cwrite (i.e. site-config)
        elif (answer == "/"):
            cwrite.delete(category_id,variable_id)
            print ("%s reverted to %s" %(varname,default_value))
            return
        elif (answer == ">"):
            if support_next:
                raise Exception ('NextCategory')
            else:
                print "No support for next category"
        else:
            if cdef.validate_type(variable_type, answer):
                variable['value'] = answer
                cwrite.set(category,variable)
                return
            else:
                print "Not a valid value"

def prompt_variables_all (cdef, cread, cwrite, show_comments):
    try:
        for (category_id, (category, variables)) in cread.variables().iteritems():
            print ("========== Category = %s" % category_id.upper())
            for variable in variables.values():
                try:
                    newvar = prompt_variable (cdef, cread, cwrite, category, variable,
                                              show_comments, True)
                except Exception, inst:
                    if (str(inst) == 'NextCategory'): break
                    else: raise
                    
    except Exception, inst:
        if (str(inst) == 'BailOut'): return
        else: raise

def prompt_variables_category (cdef, cread, cwrite, cid, show_comments):
    cid=cid.lower()
    CID=cid.upper()
    try:
        print ("========== Category = %s" % CID)
        for vid in list_category(cdef,cid):
            (category,variable) = cdef.locate_varname(vid.upper())
            newvar = prompt_variable (cdef, cread, cwrite, category, variable,
                                      show_comments, False)
    except Exception, inst:
        if (str(inst) == 'BailOut'): return
        else: raise

####################
def show_variable (cdef, cread, cwrite,
                   category, variable,show_value,show_comments):
    assert category.has_key('id')
    assert variable.has_key('id')

    category_id = category ['id']
    variable_id = variable['id']

    default_value = get_value(cdef,category_id,variable_id)
    current_value = get_current_value(cread,cwrite,category_id,variable_id)
    varname = get_varname (cread,category_id, variable_id)
    if show_comments :
        print_name_comments (cdef, category_id, variable_id)
    if show_value:
        print "%s = %s" % (varname,current_value)
    else:
        print "%s" % (varname)

def show_variables_all (cdef, cread, cwrite, show_value, show_comments):
    for (category_id, (category, variables)) in cread.variables().iteritems():
        print ("========== Category = %s" % category_id.upper())
        for variable in variables.values():
            show_variable (cdef, cread, cwrite,
                           category, variable,show_value,show_comments)

def show_variables_category (cdef, cread, cwrite, cid, show_value,show_comments):
    cid=cid.lower()
    CID=cid.upper()
    print ("========== Category = %s" % CID)
    for vid in list_category(cdef,cid):
        (category,variable) = cdef.locate_varname(vid.upper())
        show_variable (cdef, cread, cwrite, category, variable,
                       show_value,show_comments)

####################
re_mainloop_0arg="^(?P<command>[uUwrRqlLsSeEcvVhH\?])[ \t]*$"
re_mainloop_1arg="^(?P<command>[sSeEvV])[ \t]+(?P<arg>\w+)$"
matcher_mainloop_0arg=re.compile(re_mainloop_0arg)
matcher_mainloop_1arg=re.compile(re_mainloop_1arg)

def mainloop (cdef, cread, cwrite, default_config, site_config, consolidated_config):
    global service
    while True:
        try:
            answer = raw_input("Enter command (u for usual changes, w to save, ? for help) ").strip()
        except EOFError:
            answer =""
        except KeyboardInterrupt:
            print "\nBye"
            sys.exit()

        if (answer == "") or (answer in "?hH"):
            print mainloop_usage
            continue
        groups_parse = matcher_mainloop_0arg.match(answer)
        command=None
        if (groups_parse):
            command = groups_parse.group('command')
            arg=None
        else:
            groups_parse = matcher_mainloop_1arg.match(answer)
            if (groups_parse):
                command = groups_parse.group('command')
                arg=groups_parse.group('arg')
        if not command:
            print ("Unknown command >%s< -- use h for help" % answer)
            continue

        show_comments=command.isupper()

        mode='ALL'
        if arg:
            mode=None
            arg=arg.lower()
            variables=list_category (cdef,arg)
            if len(variables):
                # category_id as the category name
                # variables as the list of variable names
                mode='CATEGORY'
                category_id=arg
            arg=arg.upper()
            (category,variable)=cdef.locate_varname(arg)
            if variable:
                # category/variable as output by locate_varname
                mode='VARIABLE'
            if not mode:
                print "%s: no such category or variable" % arg
                continue

        if command in "qQ":
            # todo check confirmation
            return
        elif command == "w":
            try:
                # Confirm that various constraints are met before saving file.
                validate_variables = g_configuration.get('validate_variables',{})
                validated_variables = cwrite.verify(cdef, cread, validate_variables)
                validator = g_configuration.get('validator',noop_validator)
                validator(validated_variables)
                cwrite.save(site_config)
            except ConfigurationException, e:
                print "Save failed due to a configuration exception: %s" % e
                break;
            except:
                print traceback.print_exc()
                print ("Could not save -- fix write access on %s" % site_config)
                break
            print ("Wrote %s" % site_config)
            consolidate(default_config, site_config, consolidated_config)
            print ("You might want to type 'r' (restart %s), 'R' (reload %s) or 'q' (quit)" % \
                   (service,service))
        elif command in "uU":
            global usual_variables
            try:
                for varname in usual_variables:
                    (category,variable) = cdef.locate_varname(varname)
                    if not (category is None and variable is None):
                        prompt_variable(cdef, cread, cwrite, category, variable, False)
            except Exception, inst:
                if (str(inst) != 'BailOut'):
                    raise
        elif command == "r":
            restart_service()
        elif command == "R":
            reload_service()
        elif command == "c":
            print_categories(cread)
        elif command in "eE":
            if mode == 'ALL':
                prompt_variables_all(cdef, cread, cwrite,show_comments)
            elif mode == 'CATEGORY':
                prompt_variables_category(cdef,cread,cwrite,category_id,show_comments)
            elif mode == 'VARIABLE':
                try:
                    prompt_variable (cdef,cread,cwrite,category,variable,
                                     show_comments,False)
                except Exception, inst:
                    if str(inst) != 'BailOut':
                        raise
        elif command in "vVsSlL":
            show_value=(command in "sSlL")
            (c1,c2,c3) = (cdef, cread, cwrite)
            if command in "lL":
                (c1,c2,c3) = (cwrite,cwrite,cwrite)
            if mode == 'ALL':
                show_variables_all(c1,c2,c3,show_value,show_comments)
            elif mode == 'CATEGORY':
                show_variables_category(c1,c2,c3,category_id,show_value,show_comments)
            elif mode == 'VARIABLE':
                show_variable (c1,c2,c3,category,variable,show_value,show_comments)
        else:
            print ("Unknown command >%s< -- use h for help" % answer)

####################
# creates directory for file if not yet existing
def check_dir (config_file):
    dirname = os.path.dirname (config_file)
    if (not os.path.exists (dirname)):
        try:
            os.makedirs(dirname,0755)
        except OSError, e:
            print "Cannot create dir %s due to %s - exiting" % (dirname,e)
            sys.exit(1)
            
        if (not os.path.exists (dirname)):
            print "Cannot create dir %s - exiting" % dirname
            sys.exit(1)
        else:
            print "Created directory %s" % dirname
                
####################
def optParserSetup(configuration):
    parser = OptionParser(usage=usage(), version="%prog " + release_rev + release_url )
    parser.set_defaults(config_dir=configuration['config_dir'],
                        service=configuration['service'],
                        usual_variables=configuration['usual_variables'])
    parser.add_option("","--configdir",dest="config_dir",help="specify configuration directory")
    parser.add_option("","--service",dest="service",help="specify /etc/init.d style service name")
    parser.add_option("","--usual_variable",dest="usual_variables",action="append", help="add a usual variable")
    return parser

def main(command,argv,configuration):
    global g_configuration
    g_configuration=configuration

    parser = optParserSetup(configuration)
    (config,args) = parser.parse_args()
    if len(args)>3:
        parser.error("too many arguments")

    configuration['service']=config.service
    configuration['usual_variables']=config.usual_variables
    configuration['config_dir']=config.config_dir
    # add in new usual_variables defined on the command line
    for usual_variable in config.usual_variables:
        if usual_variable not in configuration['usual_variables']:
            configuration['usual_variables'].append(usual_variable)

    # intialize configuration
    init_configuration()

    (default_config,site_config,consolidated_config) = (def_default_config, def_site_config, def_consolidated_config)
    if len(args) >= 1:
        default_config=args[0]
    if len(args) >= 2:
        site_config=args[1]
    if len(args) == 3:
        consolidated_config=args[2]

    for c in (default_config,site_config,consolidated_config):
        check_dir (c)

    try:
        # the default settings only - read only
        cdef = PLCConfiguration(default_config)

        # in effect : default settings + local settings - read only
        cread = PLCConfiguration(default_config)

    except ConfigurationException, e:
        print ("Error %s in default config file %s" %(e,default_config))
        return 1
    except:
        print traceback.print_exc()
        print ("default config files %s not found, is myplc installed ?" % default_config)
        return 1


    # local settings only, will be modified & saved
    cwrite=PLCConfiguration()
    
    try:
        cread.load(site_config)
        cwrite.load(site_config)
    except:
        cwrite = PLCConfiguration()

    mainloop (cdef, cread, cwrite, default_config, site_config, consolidated_config)
    return 0

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] in ['build', 'install', 'uninstall']:
        from distutils.core import setup
        setup(py_modules=["plc_config"])
