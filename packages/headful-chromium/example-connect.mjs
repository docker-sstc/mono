import { chromium } from 'playwright'

async function main(browser, f) {
  const browserContext = browser.contexts()[0] ?? await browser.newContext()
  const page = browserContext.pages()[0] ?? await browserContext.newPage()
  await page.goto('https://google.com')
  await page.pdf({ path: f })
  await browserContext.close()
}
try {
  const browser = await chromium.connect('ws://127.0.0.1:3000/')
  await main(browser, import.meta.filename + '.0.pdf')
  await browser.close()
} catch (e) {
  console.error(e)
}
try {
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9222')
  await main(browser, import.meta.filename + '.1.pdf' )
  await browser.close()
} catch (e) {
  console.error(e)
}
