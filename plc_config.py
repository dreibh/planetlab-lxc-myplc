#!/usr/bin/python
#
# Merge PlanetLab Central (PLC) configuration files into a variety of
# output formats. These files represent the global configuration for a
# PLC installation.
#
# Mark Huang <mlhuang@cs.princeton.edu>
# Copyright (C) 2006 The Trustees of Princeton University
#
# $Id: plc_config.py,v 1.2 2006/04/04 22:09:25 mlhuang Exp $
#

import xml.dom.minidom
from StringIO import StringIO
import time
import re
import textwrap
import codecs
import os
import types


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

        dom = xml.dom.minidom.parse(file)
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


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] in ['build', 'install']:
        from distutils.core import setup
        setup(py_modules=["plc_config"])
