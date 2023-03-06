odoo.define('sg_advance_request_portal.advance_portal', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var time = require('web.time');

publicWidget.registry.ApprovalPortal = publicWidget.Widget.extend({
    selector: '#wrapwrap:has(.new_advance_form, .edit_advance_form)',
    events: {
        'click .new_advance_confirm': '_onNewApprovalConfirm',
        'click .edit_advance_confirm': '_onEditApprovalConfirm',
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
    _create_advance: function () {
    	return this._rpc({
            model: 'hr.advance.salary',
            method: 'create_advance_portal',

            args: [{
                request_amount: $('.new_advance_form .request_amount').val(),
                payment: $("input[name='payment']:checked").val(),
                payment_start_date: $('.new_advance_form .payment_start_date').val(),
                reason: $('.new_advance_form .reason').val(),

            }],
        }).then(function (response) {
            if (response.errors) {
                      alert(1);
                $('#new-opp-dialog .alert').remove();
                $('#new-opp-dialog div:first').prepend('<div class="alert alert-danger">' + response.errors + '</div>');
                return Promise.reject(response);
            } else {
                window.location = '/advance/requests/form/' + response.id;
            }
            console.log('True');
        });
        console.log('True');
    },
    /**
     * @private
     * @returns {Promise}
     */
    _edit_advance: function () {
        return this._rpc({
            model: 'hr.advance.salary',
            method: 'update_advance_portal',
            args: [[parseInt($('.edit_advance_form .advance_id').val())], {
            	advanceID: parseInt($('.edit_advance_form .advance_id').val()),
            	request_amount: $('.edit_advance_form .request_amount').val(),
                date: $('.edit_advance_form .payment_start_date').val(),
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
    _onNewApprovalConfirm: function (ev) {
        ev.preventDefault();
        ev.stopPropagation();
        this._buttonExec($(ev.currentTarget), this._create_advance);
    },
    /**
     * @private
     * @param {Event} ev
     */
    _onEditApprovalConfirm: function (ev) {
        ev.preventDefault();
        ev.stopPropagation();
        this._buttonExec($(ev.currentTarget), this._edit_advance);
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
