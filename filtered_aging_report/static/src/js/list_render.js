odoo.define('filtered_aging_report.ListController', function (require) {
	var ListRender = require('web.ListRenderer')
	var session = require('web.session');
	ListRender.include({
		
		_onToggleSelection: function (event) {
			this._super(event);
			 var checked = $(event.currentTarget).prop('checked') || false;
			 session.user_context['select_all'] = checked
			
		},
		
		
		
		_onSelectRecord: function (event) {
			this._super(event)
			if (!$(event.currentTarget).find('input').prop('checked')) {
				session.user_context['select_all'] = false
			}
			}

		
		
	})
	
	
})