document.addEventListener("DOMContentLoaded", () => {
	const startBtn = document.getElementById("startBtn");
	const pauseBtn = document.getElementById("pauseBtn");
	const stopBtn = document.getElementById("stopBtn");
	const restartBtn = document.getElementById("restartBtn");
	const downloadBtn = document.getElementById("downloadBtn");
	const statusText = document.getElementById("statusText");

	chrome.storage.local.get(["monitoring"], (result) => {
		const isMonitoring = result.monitoring || false;
		updateUI(isMonitoring ? "Running" : "Stopped");
	});

	startBtn.addEventListener("click", () => {
		chrome.runtime.sendMessage({ action: "start" });
		updateUI("Running");
	});

	pauseBtn.addEventListener("click", () => {
		chrome.runtime.sendMessage({ action: "pause" });
		updateUI("Paused");
	});

	stopBtn.addEventListener("click", () => {
		chrome.runtime.sendMessage({ action: "stop" });
		updateUI("Stopped");
	});

	restartBtn.addEventListener("click", () => {
		chrome.runtime.sendMessage({ action: "restart" });
		updateUI("Running");
	});

	downloadBtn.addEventListener("click", () => {
		downloadData();
	});

	function updateUI(status) {
		statusText.textContent = status;
		if (status === "Running") {
			startBtn.disabled = true;
			pauseBtn.disabled = false;
			stopBtn.disabled = false;
			restartBtn.disabled = false;
			downloadBtn.disabled = false;
		} else if (status === "Paused") {
			startBtn.disabled = true;
			pauseBtn.disabled = true;
			stopBtn.disabled = false;
			restartBtn.disabled = false;
			downloadBtn.disabled = false;
		} else { // Stopped
			startBtn.disabled = false;
			pauseBtn.disabled = true;
			stopBtn.disabled = true;
			restartBtn.disabled = true;
			downloadBtn.disabled = false;
		}
	}

	function downloadData() {
		chrome.storage.local.get(["tabSequence", "tabHTMLCache"], (result) => {
			const tabSequence = result.tabSequence || [];
			const tabHTMLCache = result.tabHTMLCache || [];

			const data = {
				sequence: tabSequence,
				htmlContent: tabHTMLCache
			};

			const jsonString = JSON.stringify(data, null, 2);
			const blob = new Blob([jsonString], { type: "application/json" });

			const url = URL.createObjectURL(blob);
			chrome.downloads.download({
				url: url,
				filename: `tab_monitor_data_${Date.now()}.json`,
				saveAs: true
			}, () => {
				URL.revokeObjectURL(url);
			});
		});
	}
});
