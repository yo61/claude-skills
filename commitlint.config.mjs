export default {
  extends: ['@commitlint/config-conventional'],
  rules: {
    // No scope-enum: this repo is a single package (the marketplace), so scope is decorative.
    'subject-case': [0],
  },
};
