odoo.define('remove_export_option.remove_export_option', function (require) {
"use strict";
var core = require('web.core');
var QWeb = core.qweb;
var Sidebar = require('web.Sidebar');
var FormView = require('web.FormView');
var _t = core._t;
var _lt = core._lt;
var model;


//    Sidebar.include({
//        start: function () {
//            var self = this;
//            var def;
//            var export_label = _t("Export");
//            def = this.getSession().user_has_group('gestion_profil.group_receptionniste').then(function(has_group) {
//
//                if (has_group)
//                {
//                    self.items['other'] = $.grep(self.items['other'], function(i){
//                        return i && i.label && i.label != export_label;
//                    });
//                }
//            });
//            return Promise.resolve(def).then(this._super.bind(this));
//        },
//    });
    Sidebar.include({
        start: function () {
            var self = this;
            var def;
            var export_label = _t("Export");
            def = this.getSession().user_has_group('gestion_profil.group_commercial').then(function(has_group) {

                if (has_group)
                {
                    self.items['other'] = $.grep(self.items['other'], function(i){
                        return i && i.label && i.label != export_label;
                    });
                }
            });
            return Promise.resolve(def).then(this._super.bind(this));
        },
    });
    Sidebar.include({
        start: function () {
            var self = this;
            var def;
            var export_label = _t("Export");
            def = this.getSession().user_has_group('gestion_profil.group_assistante_adv').then(function(has_group) {

                if (has_group)
                {
                    self.items['other'] = $.grep(self.items['other'], function(i){
                        return i && i.label && i.label != export_label;
                    });
                }
            });
            return Promise.resolve(def).then(this._super.bind(this));
        },
    });
    Sidebar.include({
        start: function () {
            var self = this;
            var def;
            var export_label = _t("Export");
            def = this.getSession().user_has_group('gestion_profil.group_caissier').then(function(has_group) {

                if (has_group)
                {
                    self.items['other'] = $.grep(self.items['other'], function(i){
                        return i && i.label && i.label != export_label;
                    });
                }
            });
            return Promise.resolve(def).then(this._super.bind(this));
        },
    });
});
