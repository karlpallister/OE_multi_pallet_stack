# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
  "name": "Multiple Pallet Stacks",
    "version": "0.1",
	"description": """Allows each Sales Order Line to have multiple pallet stack formats, such as 2 pallets at 3 high, 1 at 4 high, and 5 loose cases. Each pallet stack may have an additional BOM, which will include, for example, a pallet, a label, stretchwrap and corner boards. This information is then propogated to the Manufacturing Orders, and adds to the Works Order BOM.""",
	"depends": ["base", "sale", "mrp_operations"],
	'author': 'Karl Pallister.',
    'website': '',
    "data": ['sale_order_line.xml'],
	"views": ['view/views.xml'],
    "installable": True,
    "active": False
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
