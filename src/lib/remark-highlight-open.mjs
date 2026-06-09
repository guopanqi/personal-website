import { visit } from 'unist-util-visit';

export default function remarkHighlightOpen() {
  return (tree) => {
    const nodesToReplace = [];
    visit(tree, 'text', (node, index, parent) => {
      if (!parent || parent.type !== 'paragraph') return;
      const match = node.value.match(/^(\s*)==([^]*)$/);
      if (!match) return;
      const content = match[2];
      if (content.includes('==')) return;
      const children = [];
      if (match[1]) children.push({ type: 'text', value: match[1] });
      children.push({
        type: 'highlight',
        data: { hName: 'mark' },
        children: [{ type: 'text', value: content }]
      });
      nodesToReplace.push([parent, node, children]);
    });
    for (const [parent, node, children] of nodesToReplace) {
      const idx = parent.children.indexOf(node);
      if (idx !== -1) parent.children.splice(idx, 1, ...children);
    }
  };
}
