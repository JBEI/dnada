module.exports = {
    parser: 'vue-eslint-parser',
    extends: [
        'plugin:@typescript-eslint/recommended',
        "eslint:recommended",
    ],
    parserOptions: {
        ecmaVersion: 2018,
        sourceType: 'module',
        "parser": '@typescript-eslint/parser',
    },
    plugins: [
        'vuetify'
    ],
    rules: {
        'vuetify/no-deprecated-classes': 'error',
        'vuetify/grid-unknown-attributes': 'error',
        'vuetify/no-legacy-grid': 'error',
    },
};
