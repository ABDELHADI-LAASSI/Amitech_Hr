{
    'name': 'Custom Login Page',
    'description': 'Customize the Odoo login page with new styles and layout.',
    'version': '1.0',
    'author': 'Abdelhadi',
    'category': 'Customizations',
    'depends': ['web'],
    'data': [
        'views/login_template.xml',
        'views/reset_password.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'custom_login/static/src/css/custom_login.css',
        ],
    },
    'installable': True,
    'application': False,
}
