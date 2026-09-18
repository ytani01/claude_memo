import { chromium } from 'playwright';

const AFTER = 'http://127.0.0.1:18899/claude_memo.html';
const BEFORE = 'http://127.0.0.1:18900/claude_memo.html';

const results = [];
function log(name, ok, detail) {
  results.push({ name, ok, detail });
  console.log((ok ? 'OK ' : 'NG ') + name + (detail ? ' :: ' + detail : ''));
}

const browser = await chromium.launch();

// ---- 1. 機能確認 (AFTER only) ----
{
  const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
  const consoleErrors = [];
  page.on('console', msg => { if (msg.type() === 'error') consoleErrors.push(msg.text()); });
  page.on('pageerror', err => consoleErrors.push('pageerror: ' + err.message));
  await page.goto(AFTER);
  await page.waitForLoadState('networkidle');

  const total = await page.textContent('#total-slides');
  log('total-slides = 17', total.trim() === '17', `got=${total}`);

  const num1 = await page.textContent('#slide-num');
  log('slide-num starts at 01', num1.trim() === '01', `got=${num1}`);

  // playlist has 17 items
  const playlistCount = await page.$$eval('#playlist-items > *', els => els.length);
  log('playlist has 17 items', playlistCount === 17, `got=${playlistCount}`);

  // click next 16 times -> reach slide 17
  for (let i = 0; i < 16; i++) {
    await page.click('#next-btn');
    await page.waitForTimeout(50);
  }
  const num17 = await page.textContent('#slide-num');
  log('after 16x next -> slide-num 17', num17.trim() === '17', `got=${num17}`);

  // click next again at last slide (should stay, no JS error)
  await page.click('#next-btn');
  await page.waitForTimeout(50);
  const numStay = await page.textContent('#slide-num');
  log('next at last slide stays at 17 (no crash)', numStay.trim() === '17', `got=${numStay}`);

  // click prev 16 times -> back to slide 1
  for (let i = 0; i < 16; i++) {
    await page.click('#prev-btn');
    await page.waitForTimeout(50);
  }
  const numBack1 = await page.textContent('#slide-num');
  log('after 16x prev -> slide-num 01', numBack1.trim() === '01', `got=${numBack1}`);

  // category/footer absent in DOM
  const hasCategoryEl = await page.$('#slide-category');
  log('#slide-category element absent', hasCategoryEl === null);
  const hasFooterEl = await page.$('footer');
  log('<footer> element absent', hasFooterEl === null);

  // SLIDE badge is right-aligned (not left) within header row
  const headerBox = await page.$eval('#player-viewport > div.flex.items-center.justify-end', el => {
    const r = el.getBoundingClientRect();
    return { left: r.left, right: r.right, width: r.width };
  });
  const badgeBox = await page.$eval('#slide-num', el => {
    const badge = el.closest('div');
    const r = badge.getBoundingClientRect();
    return { left: r.left, right: r.right };
  });
  const gapToRight = headerBox.right - badgeBox.right;
  const gapToLeft = badgeBox.left - headerBox.left;
  log('SLIDE badge sits at right edge of header (not left)', gapToRight < gapToLeft,
    `gapToRight=${gapToRight.toFixed(1)} gapToLeft=${gapToLeft.toFixed(1)}`);

  console.log('CONSOLE_ERRORS(after, functional test):', JSON.stringify(consoleErrors));
  log('no console errors during functional test', consoleErrors.length === 0, JSON.stringify(consoleErrors));

  await page.close();
}

// ---- 2. play/pause simple smoke (does it error) ----
{
  const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
  const consoleErrors = [];
  page.on('console', msg => { if (msg.type() === 'error') consoleErrors.push(msg.text()); });
  page.on('pageerror', err => consoleErrors.push('pageerror: ' + err.message));
  await page.goto(AFTER);
  await page.waitForLoadState('networkidle');
  await page.click('#play-btn');
  await page.waitForTimeout(1500);
  await page.click('#play-btn'); // pause
  await page.waitForTimeout(300);
  console.log('CONSOLE_ERRORS(after, play smoke):', JSON.stringify(consoleErrors));
  log('no console errors during play/pause smoke', consoleErrors.length === 0, JSON.stringify(consoleErrors));
  await page.close();
}

// ---- 3. overflow measurement, 4 conditions, before vs after ----
const conditions = [
  { name: 'PC 1280x800', width: 1280, height: 800, fullscreen: false },
  { name: '横持ち 844x390 通常', width: 844, height: 390, fullscreen: false },
  { name: '横持ち 844x390 フルスクリーン', width: 844, height: 390, fullscreen: true },
  { name: '縦持ち 390x844 フルスクリーン', width: 390, height: 844, fullscreen: true },
];

async function measureOverflow(url, cond) {
  const page = await browser.newPage({ viewport: { width: cond.width, height: cond.height } });
  await page.goto(url);
  await page.waitForLoadState('networkidle');
  if (cond.fullscreen) {
    // fullscreen API doesn't work headless reliably; approximate by toggling the
    // player's fullscreen class/behavior via fullscreen-btn click, then measure.
    try {
      await page.click('#fullscreen-btn');
      await page.waitForTimeout(300);
    } catch (e) {
      // ignore, headless fullscreen often unsupported
    }
  }
  const data = await page.evaluate(() => {
    const doc = document.documentElement;
    const body = document.body;
    const viewport = document.getElementById('player-viewport');
    const vBox = viewport ? viewport.getBoundingClientRect() : null;
    return {
      docScrollW: doc.scrollWidth,
      docClientW: doc.clientWidth,
      docScrollH: doc.scrollHeight,
      docClientH: doc.clientHeight,
      bodyScrollW: body.scrollWidth,
      bodyScrollH: body.scrollHeight,
      viewportRight: vBox ? vBox.right : null,
      viewportBottom: vBox ? vBox.bottom : null,
      windowInnerW: window.innerWidth,
      windowInnerH: window.innerHeight,
    };
  });
  await page.close();
  return data;
}

for (const cond of conditions) {
  const before = await measureOverflow(BEFORE, cond);
  const after = await measureOverflow(AFTER, cond);
  const overflowXBefore = before.docScrollW - before.docClientW;
  const overflowXAfter = after.docScrollW - after.docClientW;
  const overflowYBefore = before.docScrollH - before.docClientH;
  const overflowYAfter = after.docScrollH - after.docClientH;
  console.log(`--- ${cond.name} ---`);
  console.log(`  before: overflowX=${overflowXBefore}px overflowY=${overflowYBefore}px viewportRight=${before.viewportRight} viewportBottom=${before.viewportBottom} innerW=${before.windowInnerW} innerH=${before.windowInnerH}`);
  console.log(`  after : overflowX=${overflowXAfter}px overflowY=${overflowYAfter}px viewportRight=${after.viewportRight} viewportBottom=${after.viewportBottom} innerW=${after.windowInnerW} innerH=${after.windowInnerH}`);
  const notWorse = overflowXAfter <= overflowXBefore && overflowYAfter <= overflowYBefore;
  log(`overflow not increased: ${cond.name}`, notWorse,
    `dX=${overflowXAfter - overflowXBefore} dY=${overflowYAfter - overflowYBefore}`);
}

await browser.close();

const failed = results.filter(r => !r.ok);
console.log('SUMMARY: ' + (results.length - failed.length) + '/' + results.length + ' passed');
process.exit(failed.length > 0 ? 1 : 0);
