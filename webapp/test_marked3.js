const marked = require('marked');
const instance = new marked.Marked();
instance.use({
  renderer: {
    link(token) {
      try {
        const text = this.parser.parseInline(token.tokens);
        return `<a href="#">${text}</a>`;
      } catch (e) {
        console.error("Renderer error:", e.message);
        throw e;
      }
    }
  }
});
try {
  console.log(instance.parse('Here is a [link](../test.md)'));
} catch (e) {
  console.error("Outer error:", e.message);
}
