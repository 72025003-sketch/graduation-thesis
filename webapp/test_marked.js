const marked = require('marked');
const instance = new marked.Marked();
instance.use({
  renderer: {
    link(token) {
      console.log('Token:', token);
      return `<a href="${token.href}" class="doc-link">${token.text}</a>`;
    }
  }
});
console.log(instance.parse('Here is a [link](../test.md)'));
