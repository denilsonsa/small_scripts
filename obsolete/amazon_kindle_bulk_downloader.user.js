// ==UserScript==
// @name         Amazon Kindle Ebook Library Downloader
// @namespace    http://tampermonkey.net/
// @version      2025.02.24
// @description  Adds a button to automatically download your entire Kindle ebook library from Amazon
// @match        https://www.amazon.com/hz/mycd/digital-console/contentlist/booksAll*
// @match        https://www.amazon.nl/hz/mycd/digital-console/contentlist/booksAll*
// @grant        none
// @run-at       document-idle
// @license      MIT
// @author       Audun Kvasbø, Chris Hollindale, Denilson Sá
// ==/UserScript==

// Based on:
// https://greasyfork.org/en/scripts/527580-amazon-kindle-ebook-library-downloader/code
// https://greasyfork.org/en/scripts/527376-amazon-kindle-book-downloader/code
// See also:
// https://github.com/bellisk/BulkKindleUSBDownloader
// https://gist.github.com/akagr/f726d17d9eb36e4336fe8942c6e12ed9
// https://github.com/treetrum/amazon-kindle-bulk-downloader
//
// This script is probably obsolete by the time you are reading this.
// Amazon announced they would stop allowing downloading starting on 2025-02-26.
// https://blog.the-ebook-reader.com/2025/02/12/download-transfer-for-kindle-ebooks-going-away-on-february-26/

(function () {
	'use strict';

	// Utility: Wait for a selector to appear
	function waitForElement(selector, root = document, timeoutMs = 10000) {
		return new Promise((resolve, reject) => {
			const el = root.querySelector(selector);
			if (el) return resolve(el);

			const observer = new MutationObserver(() => {
				const foundEl = root.querySelector(selector);
				if (foundEl) {
					observer.disconnect();
					resolve(foundEl);
				}
			});

			observer.observe(root, { childList: true, subtree: true });

			setTimeout(() => {
				observer.disconnect();
				reject(`Timeout waiting for ${selector}`);
			}, timeoutMs);
		});
	}

	// Helper: Click an element when it’s found
	async function clickWhenReady(selector, root = document, timeoutMs = 10000) {
		try {
			const el = await waitForElement(selector, root, timeoutMs);
			el.click();
			//console_log('Clicked', selector);
		} catch (error) {
			console_warn(`Selector ${selector} not found within ${timeoutMs}ms. Skipping...`);
		}
	}

	window.BULKLOG = [];
	function console_log(foo) {
		window.BULKLOG.push(foo);
		console.log(foo);
	}
	function console_warn(foo) {
		window.BULKLOG.push('WARN: ' + foo);
		console.warn(foo);
	}

	// Process all dropdowns for the current page
	async function processDropdowns() {
		// Requery dropdowns on each page
		const dropdowns = [...document.querySelectorAll('[class^="Dropdown-module_container__"]')];

		// Limit the number of dropdowns for testing or processing
		const toDownload = dropdowns.length;

		const currentPageNumber = document.querySelector('.page-item.active').textContent.trim();

		console_log(`Processing ${toDownload} dropdowns on page ${currentPageNumber}...`);
 		for (let i = 0; i < toDownload; i++) {
			const dropdown = dropdowns[i];

			// Book title, which is often different than the downloaded filename.
			const tr = dropdown.closest('tr');
			const title = tr.querySelector('[id^="content-title-"]').textContent.trim();
			const author = tr.querySelector('[id^="content-author-"]').textContent.trim();
			const date = tr.querySelector('[id^="content-acquired-date-"]').textContent.trim();
			const checkbox = tr.querySelector('[class^="Checkbox"] input[type="checkbox"]');
			const id = checkbox.getAttribute('id').replace(/:KindleEBook$/, '');
			const url = `https://www.amazon.com/gp/product/${id}`;

			// Click dropdown to open it
			dropdown.click();
			console_log(`Dropdown ${i + 1}/${toDownload} opened: "${JSON.stringify({id, title, author, date, url}, null, '')}"`);

			// Is it a sample? Those cannot be downloaded.
			const tags = tr.querySelector('.information_row.tags')?.textContent.trim();
			if (tags == 'Sample') {
				console_log(`Dropdown ${i + 1}/${toDownload} ignoring because it is a SAMPLE: "${title}"`);
				continue;
			} else if (tags) {
				console_log(`Dropdown ${i + 1}/${toDownload} found tags: ${tags}`);
			}

			// Download & Transfer button
			try {
				// await clickWhenReady('[id^="DOWNLOAD_AND_TRANSFER_ACTION_"]', dropdown);
				// await clickWhenReady('div:has(>[id^="MARK_AS_READ_ACTION_"]) + div', dropdown);
				// Either MARK_AS_READ_ACTION_ or MARK_AS_UNREAD_ACTION_
				await clickWhenReady('div:has(>[id^="MARK_AS_"]) + div', dropdown);
				console_log(`Dropdown ${i + 1}/${toDownload} Download & Transfer button clicked.`);
			} catch (error) {
				console_warn(`Dropdown ${i + 1}/${toDownload} Download & Transfer button not found for this dropdown. Skipping...`);
			}

			// Choose the first Kindle in the list
			try {
				await clickWhenReady('span[id^="download_and_transfer_list_"]', dropdown);
				console_log(`Dropdown ${i + 1}/${toDownload} Download to Kindle list option selected.`);
			} catch (error) {
				console_warn(`Dropdown ${i + 1}/${toDownload} No Kindle option available in this dropdown. Skipping...`);
			}

			// Confirm download
			try {
				// await clickWhenReady('[id^="DOWNLOAD_AND_TRANSFER_ACTION_"][id$="_CONFIRM"]', dropdown);
				await clickWhenReady('[id^="DOWNLOAD_AND_TRANSFER_DIALOG_"] [id$="_CONFIRM"]', dropdown);
				console_log(`Dropdown ${i + 1}/${toDownload} Confirm Download button clicked.`);
			} catch (error) {
				console_warn(`Dropdown ${i + 1}/${toDownload} Confirm Download button not found. Skipping...`);
			}

			// Close success notification screen
			try {
				// Wait for the notification close button
				const notificationCloseButton = await waitForElement('span[id="notification-close"]', document, 15000); // Extended timeout
				if (notificationCloseButton) {
					notificationCloseButton.click();
					console_log(`Dropdown ${i + 1}/${toDownload} Notification close button clicked.`);
				}
			} catch (error) {
				console_warn(`Dropdown ${i + 1}/${toDownload} Notification close button not found or did not appear. Skipping...`);
			}

			// Wait before processing the next dropdown
			await new Promise(resolve => setTimeout(resolve, 8000));
			console_log(`Dropdown ${i + 1}/${toDownload} processed.`);
		}

		// Handle pagination for the next page
		const nextPage = document.querySelector('.pagination .page-item.active')?.nextElementSibling;

		if (nextPage) {
			// Click the next page button
			nextPage.click();
			console_log('Clicked next page... waiting for content to load.');

			// Wait for the new dropdown container to update
			await new Promise(resolve => setTimeout(resolve, 10000)); // Fallback for pagination delay
			await processDropdowns(); // Recursively process dropdowns on the next page
		} else {
			console_log('No next page found. All dropdowns processed.');
			alert("Reached the last page - we should be good!");
		}
	}

	window.addEventListener('load', () => {
		// Start script after a short delay so Amazon’s UI can settle
		// setTimeout(() => processDropdowns(), 5000);

		// Create a button in the top right of the page to trigger the action
		const button = document.createElement('button');
		button.innerText = 'Trigger Download';
		button.style.position = 'fixed';
		button.style.top = '20px';
		button.style.right = '20px';
		button.style.padding = '10px';
		button.style.fontSize = '16px';
		button.style.backgroundColor = '#4CAF50';
		button.style.color = 'white';
		button.style.border = 'none';
		button.style.borderRadius = '5px';
		button.style.cursor = 'pointer';
		button.style.zIndex = 9999;

		// Add button to the body
		document.body.appendChild(button);
		button.addEventListener('click', processDropdowns);
	});
})();

