# -*- coding: utf-8 -*-
# Copyright 2016 SYLEAM Info Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    payment_ids = fields.One2many(comodel_name='account.payment', inverse_name='payment_transaction_id', string='Payments')
    payment_count = fields.Integer(string='Payment Count', help='Number of payment', compute='_compute_payment')

    @api.multi
    def _compute_payment(self):
        for transaction in self:
            transaction.payment_count = len(transaction.payment_ids)

    def _prepare_payment_data(self):
        self.ensure_one()

        return {
            'payment_date': fields.Date.context_today(self),
            'payment_type': 'inbound',
            'amount': self.amount - self.fees,
            'currency_id': self.currency_id.id,
            'journal_id': self.acquirer_id.journal_id.id,
            'partner_type': 'customer',
            'partner_id': self.partner_id.id,
            'payment_reference': self.reference,
            'payment_method_id': self.acquirer_id.payment_method_id.id,
            'payment_transaction_id': self.id,
            'communication': self.acquirer_reference or self.reference,
            'payment_difference_handling': 'reconcile',
            'writeoff_account_id': self.acquirer_id.writeoff_account_id.id,
        }

    @api.multi
    def _generate_and_pay_invoice(self):
        if self.acquirer_id.payment_method_id:
            self.env['account.payment'].create(self._prepare_payment_data()).post()
        else:
            super(PaymentTransaction, self)._generate_and_pay_invoice()
