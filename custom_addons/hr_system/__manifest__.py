{
    "name": "AMITECH HR",
    "author": "Abdelhadi Laassi",
    "category": "",
    "version": "1.0",
    "license": "LGPL-3",
    "depends": ['base','mail','hr', 'hr_holidays'],
    "data": [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/base_menu.xml',
        'views/hr_leave/hr_leave_view.xml',
        'views/frais_deplacement_view.xml',
        'views/avance_salaire_view.xml',
        'views/demande_document_travail_view.xml',
        'views/user/gestion_sortie/gestion_sortie_user_view.xml',
        'views/user/demande_hours_supp/demande_hours_supp_user_view.xml',
        'views/user/note_frais/note_frais_user_view.xml',
        'views/user/order_mission/order_mission_user_view.xml',
        # manager
        'views/manager/gestion_sortie/gestion_sortie_manager_view.xml',
        'views/manager/gestion_sortie/wizard_reject_sortie_view.xml',
        'views/manager/demande_hours_supp/demande_hours_supp_manager_view.xml',
        'views/manager/demande_hours_supp/wizard_reject_hours_sup.xml',
        'views/manager/note_frais/notes_frais_manager_view.xml',
        'views/manager/note_frais/note_frais_manager.xml',
        'views/manager/order_mission/order_mission_manager_view.xml',
        'views/wizards/frais_deplacement/manager_wizard.xml',
        'views/wizards/avance_salaire/manager_wizard.xml',
        #manager chef
        'views/wizards/frais_deplacement/manager_chef_wizard.xml',
        'views/wizards/avance_salaire/manager_chef_wizard.xml',
        # hr
        'views/hr/gestion_sortie/gestion_sortie_hr_view.xml',
        'views/hr/gestion_sortie/wizard_reject_sortie_view.xml',
        'views/hr/demande_hours_supp/demande_hours_supp_hr_view.xml',
        'views/hr/demande_hours_supp/wizard_reject_hours_sup.xml',
        'views/hr/note_frais/note_frais_hr_view.xml',
        'views/hr/note_frais/note_frais_wizard.xml',
        'views/hr/order_mission/order_mission_hr_view.xml',
        'views/wizards/frais_deplacement/hr_wizard.xml',
        'views/wizards/avance_salaire/hr_wizard.xml',
        'views/wizards/document_Travail/hr_wizard.xml',
        # hr configuration
        'views/hr/configuration/type_heures_supp.xml',
        'views/hr/configuration/type_frais_view.xml',
        'views/hr/configuration/type_order_mission_view.xml',
        'views/hr/configuration/type_frais_deplacement_view.xml',
        'views/hr/configuration/type_avance_salaire_view.xml',
        'views/hr/configuration/type_document_travail_view.xml',
        #finance
        'views/wizards/frais_deplacement/finance_wizard.xml',
        'views/wizards/avance_salaire/finance_wizard.xml',
        'report/conge_report.xml'
    ],


    "assets": {
        "web.assets_backend": ['hr_system/static/src/css/style.css'],
        "web.report_assets_common": [],
    },
    'installable': True,
    'application': True,
}
