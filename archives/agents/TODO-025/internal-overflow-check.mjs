import { chromium } from 'playwright';

const AFTER = 'http://127.0.0.1:18899/claude_memo.html';

const conditions = [
  { name: 'PC 1280x800', width: 1280, height: 800, fullscreen: false },
  { name: '横持ち 844x390 通常', width: 844, height: 390, fullscreen: false },
  { name: '横持ち 844x390 フルスクリーン', width: 844, height: 390, fullscreen: true },
  { name: '縦持ち 390x844 フルスクリーン', width: 390, height: 844, fullscreen: true },
];

const browser = await chromium.launch();

for (const cond of conditions) {
  const page = await browser.newPage({ viewport: { width: cond.width, height: cond.height } });
  await page.goto(AFTER);
  await page.waitForLoadState('networkidle');
  await page.click('#next-btn'); // -> slide 2
  await page.waitForTimeout(200);
  if (cond.fullscreen) {
    try {
      await page.click('#fullscreen-btn');
      await page.waitForTimeout(300);
    } catch (e) {}
  }
  const data = await page.evaluate(() => {
    const canvas = document.getElementById('slide-canvas');
    const viewport = document.getElementById('player-viewport');
    const cRect = canvas.getBoundingClientRect();
    const vRect = viewport.getBoundingClientRect();
    // the grid of 6 cards is the first child div inside canvas's inner wrapper
    const grid = canvas.querySelector('.grid');
    const gRect = grid ? grid.getBoundingClientRect() : null;
    return {
      canvasScrollH: canvas.scrollHeight,
      canvasClientH: canvas.clientHeight,
      canvasScrollW: canvas.scrollWidth,
      canvasClientW: canvas.clientWidth,
      canvasRect: { top: cRect.top, bottom: cRect.bottom, left: cRect.left, right: cRect.right },
      viewportRect: { top: vRect.top, bottom: vRect.bottom, left: vRect.left, right: vRect.right },
      gridRect: gRect ? { top: gRect.top, bottom: gRect.bottom, left: gRect.left, right: gRect.right } : null,
    };
  });
  await page.close();
  const internalOverflowY = data.canvasScrollH - data.canvasClientH;
  const internalOverflowX = data.canvasScrollW - data.canvasClientW;
  const gridBelowViewport = data.gridRect ? data.gridRect.bottom - data.viewportRect.bottom : null;
  const gridAboveCanvasTop = data.gridRect ? data.canvasRect.top - data.gridRect.top : null;
  console.log(`--- ${cond.name} ---`);
  console.log(`  slide-canvas internalOverflow: X=${internalOverflowX}px Y=${internalOverflowY}px`);
  console.log(`  grid.bottom - viewport.bottom = ${gridBelowViewport}px (positive = grid sticks out below viewport)`);
  console.log(`  canvas.top - grid.top = ${gridAboveCanvasTop}px (positive = grid clipped above canvas top)`);
  console.log(`  canvasRect=${JSON.stringify(data.canvasRect)}`);
  console.log(`  viewportRect=${JSON.stringify(data.viewportRect)}`);
  console.log(`  gridRect=${JSON.stringify(data.gridRect)}`);
}

await browser.close();
