export default {
  extends: ['@commitlint/config-conventional'],
  // Dependabot auto-generates commit bodies with long markdown URLs that exceed
  // body-max-line-length. It won't wrap them, so skip linting its commits while
  // keeping the full ruleset enforced for human authors.
  ignores: [(message) => message.includes('Signed-off-by: dependabot[bot]')],
  rules: {
    // No scope-enum: this repo is a single package (the marketplace), so scope is decorative.
    'subject-case': [0],
  },
};
