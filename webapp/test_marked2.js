const marked = require('marked');
const instance = new marked.Marked();
instance.use({
  renderer: {
    link(token) {
      const href = token.href || '';
      console.log('Has parser?', !!this.parser);
      return `<a href="${href}">${token.text}</a>`;
    }
  }
});
try {
  console.log(instance.parse('Here is a [link](../test.md)'));
} catch (e) {
  console.error("ERROR:", e.message);
}
