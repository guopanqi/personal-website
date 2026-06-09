import { defineConfig } from 'astro/config';
import remarkGfm from 'remark-gfm';
import remarkFootnotes from './src/lib/remark-footnotes.mjs';
import remarkBreaks from 'remark-breaks';
import { remarkHighlightMark } from 'remark-highlight-mark';
import remarkHighlightOpen from './src/lib/remark-highlight-open.mjs';
import remarkImageSize from './src/lib/remark-image-size.mjs';

const repo = process.env.GITHUB_REPOSITORY?.split('/')[1] ?? '';
const owner = process.env.GITHUB_REPOSITORY_OWNER ?? '';
const isUserSite = repo.endsWith('.github.io');
const base = process.env.GITHUB_ACTIONS && repo && !isUserSite ? `/${repo}` : '/';
const site =
  process.env.SITE_URL ||
  (owner ? `https://${owner}.github.io` : 'https://example.com');

export default defineConfig({
  site,
  base,
  markdown: {
    remarkPlugins: [remarkGfm, remarkBreaks, remarkHighlightMark, remarkHighlightOpen, remarkImageSize, remarkFootnotes],
    remarkRehype: {
      handlers: {
        highlight(state, node) {
          const result = { type: 'element', tagName: 'mark', properties: {}, children: state.all(node) };
          return result;
        }
      }
    }
  },
  image: {
    service: {
      entrypoint: 'astro/assets/services/noop'
    }
  }
});
