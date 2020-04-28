#_*_ coding:utf-8 _*_

'''
My_custom_report.
to create custom report

'''
from odoo import models, api, _

class RoportMyReport(models.AbstractModel):
    _name = "account.my.report"
    _inherit = "account.report"
    _desription = "My custom report"
    
    
    
    
    
    #Override this methods
    
    #--- return the header of the table of the report
    def _get_columns_name(self, options):
        '''
        return a list of dict objects that represents the header of the header
        of the report.
            - Each element of the list correspond to a column in the report
            - Each element must be a dict with following keys
                + Name (mandadory): the name that will be shown as column header, key must be present
                  but can have an empty value
                + Class (Optionnal): CSS class to had to the column
                + Style (Optionnal): inline CSS style to add to the column
                
                
        '''
        pass
    
    #return the lines of the report
    @api.model
    def _get_lines(self, options, lines_ids=None):
        '''
        this method should return the list of tlines of the report. The line_id parameter is
        set when unfolding a line in the report, in this case this method should only return
        a subset of the lines corresponding to line_id and its domain, nothing else.
            - The order of the list is the order in wich the lines will be displayed in the report
            - Each line of the dict is a dictionnary structure with the specific keys
            
        Dictionnary for each can contain the following information:
            - id : id of the line. Referenced for footnote, unfolding, etc.
            - name: what will be displayed in the first column
            - colspan: use this if you want the name to span over many column
            - column: a list of column values
            - class: css class to add to the of the table
            - unfoldable: True if the line can be unfolded
            - unfolded: True if the line has already been unfolded
            - parent_id: id of the parent line if this line is part of unfolded block
            - level: determine the layout (should be between 0-9 or None)
            - action_id: information passed to action
                + action_id must be the id of en existing "ir.actions_actions"
                    -Can be use to open another report
                    -or any standard action in Odoo
                + In the case action is another accounting report, the filter option will be kept between the to reports
            - caret_options: options that are displayed in dropdown for each line in report view (open invoice, open tax, annotate)
        
        action_id: 
        
        caret_options. If this option is set, a dropdown will be shown next to the line with some possible choices depending on
        the value set to catret_options
        '''
        
        pass
    
    #Name of the report that will be shown in the view and 
    #name of the file use when printing (space are remplace by _)
    def _get_report_name(self):
        return _('awesome_report')
    
    #optionnaly, if custom templates needs to be specified
    def _get_templates(self):
        return super(ReportMyReport, self).get_templates()
    
    '''
    LAST STEP
    
    Create the client action and menuitem for your report so that our report can be accessible via Odoo.
    '''