const { chromium } = require('playwright');
const path = require('path');

async function verifyScreens() {
  const browser = await chromium.launch({ headless: true });
  const viewports = [
    { name: 'PC_Edge_1080p', width: 1920, height: 1080, isMobile: false },
    { name: 'PC_Edge_1440p_2K', width: 2560, height: 1440, isMobile: false },
    { name: 'PC_Laptop_1366x768', width: 1366, height: 768, isMobile: false },
    { name: 'Samsung_Galaxy_S26_Ultra', width: 412, height: 915, isMobile: true, hasTouch: true },
    { name: 'Tablet_iPad_Pro', width: 1024, height: 1366, isMobile: false }
  ];

  const htmlPath = 'file:///' + path.resolve('apps/excalibur-s26-orb/index.html').replace(/\\\\/g, '/');
  console.log('Testing Excalibur ChatGPT-Style UI at:', htmlPath);

  let passedAll = true;

  for (const vp of viewports) {
    const context = await browser.newContext({
      viewport: { width: vp.width, height: vp.height },
      isMobile: vp.isMobile,
      hasTouch: vp.hasTouch || false
    });
    const page = await context.newPage();
    await page.goto(htmlPath, { waitUntil: 'domcontentloaded', timeout: 10000 });

    const metrics = await page.evaluate(() => {
      const app = document.getElementById('appLayout');
      const rect = app ? app.getBoundingClientRect() : document.body.getBoundingClientRect();
      const bodyWidth = document.body.scrollWidth;
      const windowWidth = window.innerWidth;
      const windowHeight = window.innerHeight;
      const voiceBtn = document.getElementById('voiceMicBtn')?.getBoundingClientRect();
      const sendBtn = document.getElementById('sendMessageBtn')?.getBoundingClientRect();
      const heroAvatar = document.querySelector('.hero-avatar-img')?.getAttribute('src');
      const bioTimer = document.getElementById('bioTimer')?.textContent.trim();
      const input = document.getElementById('chatInput');

      return {
        containerRect: { width: rect.width, height: rect.height },
        windowSize: { width: windowWidth, height: windowHeight },
        bodyScrollWidth: bodyWidth,
        hasHorizontalOverflow: bodyWidth > windowWidth,
        voiceBtn,
        sendBtn,
        hasHeroAvatar: Boolean(heroAvatar),
        bioTimer,
        inputPlaceholder: input?.placeholder
      };
    });

    console.log('\n========================================');
    console.log('📑 Viewport:', vp.name, '(' + vp.width + 'x' + vp.height + ')');
    console.log('   Container Size:', Math.round(metrics.containerRect.width) + 'x' + Math.round(metrics.containerRect.height));
    console.log('   Horizontal Overflow:', metrics.hasHorizontalOverflow ? '❌ FAIL (Overflow)' : '✅ OK (No Overflow)');
    console.log('   Hero Avatar Image Present:', metrics.hasHeroAvatar ? '✅ OK' : '❌ FAIL');
    console.log('   Bio Timer Initialized:', metrics.bioTimer);
    console.log('   Touch Target - Voice Mic:', metrics.voiceBtn ? Math.round(metrics.voiceBtn.width) + 'x' + Math.round(metrics.voiceBtn.height) + 'px' : 'N/A');
    console.log('   Touch Target - Send Btn:', metrics.sendBtn ? Math.round(metrics.sendBtn.width) + 'x' + Math.round(metrics.sendBtn.height) + 'px' : 'N/A');

    // Test sending a vocal-to-command directive
    await page.fill('#chatInput', '//STATUS probe vps mesh');
    await page.click('#sendMessageBtn');
    await page.waitForTimeout(1500);

    const messageCount = await page.evaluate(() => document.querySelectorAll('.message-row').length);
    console.log('   Conversational Message Flow (User + AI):', messageCount >= 2 ? '✅ OK (' + messageCount + ' messages rendered)' : '❌ FAIL');

    // Test prompt starter card click and new session reset
    if (vp.isMobile) {
      await page.click('#sidebarToggleBtn');
      await page.waitForTimeout(200);
    }
    await page.click('#newSessionBtn');
    await page.waitForTimeout(300);
    const heroVisibleAfterReset = await page.evaluate(() => {
      const hero = document.getElementById('heroWelcome');
      return hero && window.getComputedStyle(hero).display !== 'none';
    });
    console.log('   New Session Reset:', heroVisibleAfterReset ? '✅ OK' : '❌ FAIL');

    if (metrics.hasHorizontalOverflow || !metrics.hasHeroAvatar || messageCount < 2 || !heroVisibleAfterReset) {
      passedAll = false;
    }

    await context.close();
  }

  await browser.close();
  console.log('\n======================================');
  console.log('🎯 OVERALL VERIFICATION STATUS:', passedAll ? '✅ ALL SCREEN SIZES & CHATGPT-STYLE UI PASSED' : '❌ SOME TESTS FAILED');
}

verifyScreens().catch(err => { console.error('Verification error:', err); process.exit(1); });

