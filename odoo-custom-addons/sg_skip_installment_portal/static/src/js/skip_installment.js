odoo.define('sg_skip_installment_portal.skip_installment', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var time = require('web.time');

publicWidget.registry.SkipPortal = publicWidget.Widget.extend({
    selector: '#wrapwrap:has(.new_skip_form, .edit_skip_form)',
    events: {
        'click .new_skip_confirm': '_onNewSkipConfirm',
        'click .edit_skip_confirm': '_onEditSkipConfirm',
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @private
     * @param {jQuery} $btn
     * @param {function} callback
     * @returns {Promise}
     */
    _buttonExec: function ($btn, callback) {
        // TODO remove once the automatic system which does this lands in master
        $btn.prop('disabled', true);
        return callback.call(this).guardedCatch(function () {
            $btn.prop('disabled', false);
        });
    },
    /**
     * @private
     * @returns {Promise}
     */
    _create_skip: function () {
    	return this._rpc({
            model: 'hr.skip.installment',
            method: 'create_skip_portal',
            args: [{

                advance_salary_id: $('.new_skip_form .advance_my_select').val(),
                date: $('.new_skip_form .start_date').val(),
                name: $('.new_skip_form .name').val(),

            }],

        }).then(function (response) {
            if (response.errors) {
                      alert(1);
                $('#new-opp-dialog .alert').remove();
                $('#new-opp-dialog div:first').prepend('<div class="alert alert-danger">' + response.errors + '</div>');
                return Promise.reject(response);
            } else {
                window.location = '/skip/requests/form/' + response.id;
            }
            console.log('True');
        });
        console.log('True');
    },
    /**
     * @private
     * @returns {Promise}
     */
    _edit_skip: function () {
        return this._rpc({
            model: 'hr.skip.installment',
            method: 'update_skip_portal',
            args: [[parseInt($('.edit_skip_form .skip_id').val())], {
            	skipID: parseInt($('.edit_skip_form .skip_id').val()),
                date: $('.edit_skip_form .start_skip_date').val(),
                name: $('.edit_skip_form .name').val(),
            }],
        }).then(function () {
            window.location.reload();
        });
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     * @param {Event} ev
     */
    _onNewSkipConfirm: function (ev) {
        ev.preventDefault();
        ev.stopPropagation();
        this._buttonExec($(ev.currentTarget), this._create_skip);
    },
    /**
     * @private
     * @param {Event} ev
     */
    _onEditSkipConfirm: function (ev) {
        ev.preventDefault();
        ev.stopPropagation();
        this._buttonExec($(ev.currentTarget), this._edit_skip);
    },

//    _parse_date: function (value) {
//        console.log(value);
//        var date = moment(value, "YYYY-MM-DD", true);
//        if (date.isValid()) {
//            return time.date_to_str(date.toDate());
//        }
//        else {
//            return false;
//        }
//    },
});
});
