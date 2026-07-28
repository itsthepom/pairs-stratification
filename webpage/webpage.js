/*************************************************************************/
// Function to build a rankings table
function buildRankingTable(extraHeader, rankingsTable) {
	// Create table
	const table = document.createElement('table');
	table.border = '1';
	table.style.borderCollapse = 'collapse';
	table.style.width = '100%'
	table.className = 'rankingstable'

	// Build the table header, starting with the direction for 2 winner events
	if (extraHeader != null) {
		const thead = document.createElement('thead');
		const headerRow = document.createElement('tr');
		const th = document.createElement('th');
		th.textContent = extraHeader;
		th.setAttribute("colspan", "10");
		headerRow.appendChild(th);
		thead.appendChild(headerRow);
		table.appendChild(thead);
	}

	// Followed by the two header rows
	{
		const thead = document.createElement('thead');
		const headerRow = document.createElement('tr');
		['', '', '', '', '', 'Master', 'Small', 'Grand'].forEach(headerText => {
			const th = document.createElement('th');
			th.textContent = headerText;
			headerRow.appendChild(th);
		});
		thead.appendChild(headerRow);
		table.appendChild(thead);
	}
	{
		const thead = document.createElement('thead');
		const headerRow = document.createElement('tr');
		['Pos', 'Pair#', 'Strat', 'Pair', 'Score', 'Points', 'Slams', 'Slams'].forEach(headerText => {
			const th = document.createElement('th');
			th.textContent = headerText;
			headerRow.appendChild(th);
		});
		thead.appendChild(headerRow);
		table.appendChild(thead);
	}

	// Create the table body
	const tbody = document.createElement('tbody');
	rowNum = 0;							// Used to stripe the table
	rankingsTable.forEach(item => {
		const row = document.createElement('tr');
		// Add the position and pair number
		[item.pos, item.pairnum, item.strat].forEach(cellText => {
			const td = document.createElement('td');
			td.textContent = cellText;
			td.className = 'itemc';
			row.appendChild(td);
		});
		// Add the pair names as a link to generate the personal score cards
		{
			const td = document.createElement('td');
			const link = document.createElement('a');
			link.href = '#';
			link.textContent = item.pair;
			link.addEventListener('click', function(event) {
				event.preventDefault();
				nameClick(item.pairnum);
			});
			td.appendChild(link);
			td.className = 'item';
			row.appendChild(td);
		}
		// Add the scores
		{
			const td = document.createElement('td');
			td.textContent = item.score + '/' + item.max + ' = ' + item.percent + '%';
			td.className = 'itemc';
			row.appendChild(td);
		}
		// Add matchpoints
		{
			const td = document.createElement('td');
			td.textContent = item.mps;
			td.className = 'itemc';
			row.appendChild(td);
		}
		// Add the number of slams, leaving the cell empty if none
		{
			const td = document.createElement('td');
			if (item.ss != 0) {
				td.textContent = item.ss;
			}
			td.className = 'itemc';
			row.appendChild(td);
		}
		{
			const td = document.createElement('td');
			if (item.gs != 0) {
				td.textContent = item.gs;
			}
			td.className = 'itemc';
			row.appendChild(td);
		}
		// Stripe the table on even rows using a class on the row element
		rowNum++;
		if (rowNum % 2 === 0) {
			row.className = 'even';
		}
		// Glue the newly created row into the table body
		tbody.appendChild(row);
	});
	// Results table built. Append the body onto the table element
	table.appendChild(tbody);
	// And wrap the whole thing in a div, returning that
	const div = document.createElement('div');
	div.setAttribute("class", "rtablediv");
	div.append(table);
	return div;
}

/*************************************************************************/
// Function to build a scorecard table
function buildScorecardTable(pairnum) {
	istwowinner = eventInfo.istwowinner;
	boardsperround = eventInfo.boardsperround;

	// Create table
	const table = document.createElement('table');
	table.className = 'scorecardtable'

	// Build the table header, starting with the pair name
	pairname = getPairName(pairnum);
	{
		const thead = document.createElement('thead');
		const headerRow = document.createElement('tr');
		const th = document.createElement('th');
		th.setAttribute("colspan", istwowinner ? "11" : "12");
		if (pairname != null) {
			th.textContent = 'Pair ' + pairnum + ' - ' + pairname;
		}
		headerRow.appendChild(th);
		thead.appendChild(headerRow);
		table.appendChild(thead);
	}

	// Followed by the header row
	{
		const thead = document.createElement('thead');
		const headerRow = document.createElement('tr');
		{
			const th = document.createElement('th');
			th.textContent = 'Bd';
			headerRow.appendChild(th);
		}
		if (!istwowinner) {
			const th = document.createElement('th');
			th.textContent = 'Dir';
			headerRow.appendChild(th);
		}
		{
			const th = document.createElement('th');
			th.textContent = 'Opps';
			th.colSpan = 2;
			headerRow.appendChild(th);

		}
		['Ctrt', 'By', 'Lead', 'Tks', '+', '-', 'Pts', '%'].forEach(headerText => {
			const th = document.createElement('th');
			th.textContent = headerText;
			headerRow.appendChild(th);
		});
		thead.appendChild(headerRow);
		table.appendChild(thead);
	}

	// Create the table body
	const tbody = document.createElement('tbody');
	rowNum = 0;							// Used to stripe the table
	scorecard = null;
	scorecards.forEach(item => {
		if (item.pairnum == pairnum) {
			scorecard = item;
		}
	});
	// Function to create and return a link for the personal scorecard
	function createLink(linkText, boardNum, pairnum) {
		const link = document.createElement('a');
		link.href = '#';
		link.textContent = linkText;
		if (linkText == '') {
			link.className = 'blanklink';
		}
		link.addEventListener('click', function(event) {
			event.preventDefault();
			boardClick(boardNum, pairnum);
		});
		return link;
	}
	scorecard.board.forEach(item => {
		// Create a link to the board
		const row = document.createElement('tr');
		const link = document.createElement('a');
		link.href = '#';
		link.addEventListener('click', function(event) {
			event.preventDefault();
			boardClick(item.boardNum, pairnum);
		});
		// Add the board number
		{
			const td = document.createElement('td');
			td.className = 'itemc';
			td.appendChild(createLink(item.boardNum, item.boardNum, pairnum));
			row.appendChild(td);
		}
		if (!istwowinner) {
			const td = document.createElement('td');
			td.className = 'itemc';
			td.appendChild(createLink(item.isNS ? "N/S" : "E/W", item.boardNum, pairnum));
			row.appendChild(td);
		}
		// Add the opps info only at the start of each round
		if (rowNum % boardsperround === 0) {
			const td = document.createElement('td');
			td.className = 'itemc';
			td.appendChild(createLink(item.versus, item.boardNum, pairnum));
			td.rowSpan = boardsperround;
			row.appendChild(td);
			pairname = getPairName(item.versus);
			{
				const td = document.createElement('td');
				td.appendChild(createLink((pairname != null) ? pairname : '', item.boardNum, pairnum));
				td.rowSpan = boardsperround;
				td.className = 'item';
				row.appendChild(td);
			}
		}
		[item.contract, item.by, item.lead, item.tricks, item.plus, item.minus, item.pts].forEach(scoreitem => {
			const td = document.createElement('td');
			td.className = 'itemc';
			td.appendChild(createLink(scoreitem, item.boardNum, pairnum));
			row.appendChild(td);
		});
		{
			const td = document.createElement('td');
				if (item.percent < 20) {
					td.className = 'colorlolo';
				}
				else if (item.percent < 40) {
					td.className = 'colorlo';
				}
				else if (item.percent <= 60) {
					td.className = 'colormed';
				}
				else if (item.percent < 80) {
					td.className = 'colorhi';
				}
				else {
					td.className = 'colorhihi'
				}
			td.appendChild(createLink(item.percent, item.boardNum, pairnum));
			row.appendChild(td);
		}

		// Stripe the table on even rows using a class on the row element
		rowNum++;
		if (rowNum % 2 === 0) {
			row.className = 'even';
		}
		// Glue the newly created row into the table body
		tbody.appendChild(row);
	});
	// Scorecard table built. Append the body onto the table element
	table.appendChild(tbody);
	// And wrap the whole thing in a div, returning that
	const div = document.createElement('div');
	div.setAttribute("class", "stablediv");
	div.appendChild(table);
	return div;
}

/*************************************************************************/
// Function to build a hand content
function buildHand(handDeal, className) {
	const td = document.createElement('td');
	td.className = className;
	// Use unicode chars for the suit symbols
	td.innerHTML = '<span class="ssym">&#x2660;&nbsp;</span>' + handDeal[0] +
					 '<br><span class="ssym" style="color:red">&#x2665;&nbsp;</span>' + handDeal[1] +
					 '<br><span class="ssym" style="color:red">&#x2666;&nbsp;</span>' + handDeal[2] +
					 '<br><span class="ssym">&#x2663;&nbsp;</span>' + handDeal[3];
	return td;
}

/*************************************************************************/
// Function to build a double-dummy result row content
function buildDDRow(directionName, ddRowData, className) {
	const ddRow = document.createElement('tr');
	ddRow.className = className;
	{
		const td = document.createElement('td');
		td.textContent = directionName;
		ddRow.appendChild(td);
	}
	{
		const td = document.createElement('td');
		var tricks = ddRowData[0] - 6;
		td.textContent = tricks <= 0 ? '-' : tricks;
		ddRow.appendChild(td);
	}
	{
		const td = document.createElement('td');
		var tricks = ddRowData[1] - 6;
		td.textContent = tricks <= 0 ? '-' : tricks;
		ddRow.appendChild(td);
	}
	{
		const td = document.createElement('td');
		var tricks = ddRowData[2] - 6;
		td.textContent = tricks <= 0 ? '-' : tricks;
		ddRow.appendChild(td);
	}
	{
		const td = document.createElement('td');
		var tricks = ddRowData[3] - 6;
		td.textContent = tricks <= 0 ? '-' : tricks;
		ddRow.appendChild(td);
	}
	{
		const td = document.createElement('td');
		var tricks = ddRowData[4] - 6;
		td.textContent = tricks <= 0 ? '-' : tricks;
		ddRow.appendChild(td);
	}
	return ddRow;
}

/*************************************************************************/
// Function to build a deal table
function buildDeal(boardNum) {
	// Find the deal data for the given board number
	boardData = deals[boardNum];
	deal = boardData.deal;
	tricks = boardData.tricks;

	// Create table
	const table = document.createElement('table');
	table.className = 'dealtable'

	// Build table header, starting with the board details
	{
		const thead = document.createElement('thead');
		const headerRow = document.createElement('tr');
		const th = document.createElement('th');
		th.setAttribute("colspan", '4');
		th.textContent = 'Board ' + boardNum;
		headerRow.appendChild(th);
		thead.appendChild(headerRow);
		table.appendChild(thead);
	}
	// The table body is 3x4 cells
	const tbody = document.createElement('tbody');
	// Top row has board info, then North, then a blank cell
	{
		const row = document.createElement('tr');
		{
			const td = document.createElement('td');
			td.innerHTML = 'Dealer: ' + boardData.dealer + '<br>Vul: ' + boardData.vulnerability;
			td.className = 'dealinfo';
			row.appendChild(td);
		}
		{
			const td = document.createElement('td');
			row.appendChild(td);
		}
		row.append(buildHand(deal[0], 'northhand'));
		{
			const td = document.createElement('td');
			row.appendChild(td);
		}
		tbody.appendChild(row);
	}
	// Middle row has West, then board, then East
	{
		const row = document.createElement('tr');
		row.append(buildHand(deal[3], 'westhand'));
		{
			const td = document.createElement('td');
			td.innerHTML = 'N<br><br>W&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;E<br><br>S';
			td.className = 'dealcenter';
			td.setAttribute('colspan', '2');
			row.appendChild(td);
		}
		row.append(buildHand(deal[1], 'easthand'));
		tbody.appendChild(row);
	}
	// Bottom row has double-dummy contracts, then South, then blank
	{
		const row = document.createElement('tr');
		{
			// The double-dummy contracts is a nested table
			const ddtable = document.createElement('table');
			ddtable.className = 'ddtable'
			const thead = document.createElement('thead');
			const headerRow = document.createElement('tr');
			{
				const th = document.createElement('th');
				headerRow.appendChild(th);
			}
			{
				const th = document.createElement('th');
				th.textContent = 'N';
				headerRow.appendChild(th);
			}
			{
				const th = document.createElement('th');
				th.textContent = 'S';
				headerRow.appendChild(th);
			}
			{
				const th = document.createElement('th');
				th.textContent = 'H';
				headerRow.appendChild(th);
			}
			{
				const th = document.createElement('th');
				th.textContent = 'D';
				headerRow.appendChild(th);
			}
			{
				const th = document.createElement('th');
				th.textContent = 'C';
				headerRow.appendChild(th);
			}
			thead.appendChild(headerRow);
			ddtable.appendChild(thead);
			const ddtbody = document.createElement('tbody');
			ddtbody.appendChild(buildDDRow('N', tricks[0], 'ddrow'));
			ddtbody.appendChild(buildDDRow('S', tricks[1], 'ddrow'));
			ddtbody.appendChild(buildDDRow('E', tricks[2], 'ddrow'));
			ddtbody.appendChild(buildDDRow('W', tricks[3], 'ddrow'));
			ddtable.appendChild(ddtbody);
			row.appendChild(ddtable);
		}
		{
			const td = document.createElement('td');
			row.appendChild(td);
		}
		row.append(buildHand(deal[2], 'southhand'));
		tbody.appendChild(row);
	}
	table.appendChild(tbody);
	return table;
}

/*************************************************************************/
// Function to build a traveller table
function buildTraveller(boardNum, pairnum) {
	// Create table
	const table = document.createElement('table');
	table.className = 'travellertable'

	// Build table header
	{
		const thead = document.createElement('thead');
		const headerRow = document.createElement('tr');
		headerRow.innerHTML = '<th>NS</th><th>EW</th><th>Ctrt</th><th>By</th><th>Lead</th><th>Tks</th><th>+</th><th>-</th><th colspan="2">MPs</th>';
		thead.appendChild(headerRow);
		table.appendChild(thead);
	}
	// Add the table rows
	const tbody = document.createElement('tbody');
	var rowNum = 1;
	travellers[boardNum].forEach(travellerLine => {
		const row = document.createElement('tr');
		[travellerLine.ns, travellerLine.ew, travellerLine.contract, travellerLine.by, travellerLine.lead, travellerLine.tricks].forEach(lineitem => {			const td = document.createElement('td');
			td.textContent = lineitem;
			row.appendChild(td);
		});
		[travellerLine.plus, travellerLine.minus].forEach(lineitem => {
			const td = document.createElement('td');
			td.textContent = lineitem;
			td.className = 'scorecell'
			row.appendChild(td);
		});
		[travellerLine.nsmps, travellerLine.ewmps].forEach(lineitem => {
			const td = document.createElement('td');
			td.textContent = lineitem;
			row.appendChild(td);
		});
		// Stripe the table on even rows using a class on the row element
		rowNum++;
		if (travellerLine.ns == pairnum || travellerLine.ew == pairnum) {
			// On the row for this pair, highlight it.
			row.className = 'hilite';
		}
		else {
			if (rowNum % 2 === 0) {
				row.className = 'even';
			}
		}
		tbody.appendChild(row);
	});
	table.appendChild(tbody);
	return table;
}

/*************************************************************************/
// Function to output a single rankings section
function renderOneRanking(container, rankingDataNS, rankingDataEW) {
	// Set the page type title
	const typeHeading = document.createElement('h2');
	typeHeading.id = 'contenthead';
	typeHeading.textContent = rankingDataNS.heading;
	container.appendChild(typeHeading);

	// Render the N/S results. 'extraHeader' remains unset for a single winner event
	extraHeader = null
	if (rankingDataEW !== null) {
		extraHeader = 'North/South'
	}
	// Add table to container
	container.appendChild(buildRankingTable(extraHeader, rankingDataNS.data));

	// Render the E/W results - only for 2 winner events
	if (rankingDataEW !== null) {
		extraHeader = 'East/West'
		// Add table to container
		container.appendChild(buildRankingTable(extraHeader, rankingDataEW.data));
	}
}

/*************************************************************************/
// Function to render content from JSON
function renderContent() {
	// Clear out the container first
	const container = document.getElementById('content');
	container.innerHTML = ''; // Clear previous content

	// Set the title (appears in the browser tab)
	const title = document.getElementById('title');
	title.innerHTML = ''; // Clear previous content
	title.textContent = eventInfo.eventname;

	// Set the club name and event title for the page
	const clubHeading = document.getElementById('clubname');
	clubHeading.textContent = eventInfo.clubname;
	const eventHeading = document.getElementById('eventname');
	eventHeading.textContent = eventInfo.eventname;

	renderOneRanking(container, rankings, typeof rankingsew !== 'undefined' ? rankingsew : null);
	if (typeof rankings1 !== 'undefined') {
		renderOneRanking(container, rankings1, typeof rankingsew1 !== 'undefined' ? rankingsew1 : null);
		if (typeof rankings2 !== 'undefined') {
			renderOneRanking(container, rankings2, typeof rankingsew2 !== 'undefined' ? rankingsew2 : null);
		}
	}
}

/*************************************************************************/
function nameClick(pairnum) {
	// Clear out the container first
	const container = document.getElementById('content');
	container.innerHTML = ''; // Clear previous content

	// Set the page type title
	const typeHeading = document.createElement('h2');
	typeHeading.id = 'contenthead';
	typeHeading.textContent = 'Personal Scorecard';
	container.appendChild(typeHeading);

	// Create back link
	const backdiv = document.createElement('div');
	backdiv.className = "backlink";
	const backlink = document.createElement('a');
	backlink.href = '#';
	backlink.onclick = function(event) { event.preventDefault(); renderContent() };
	backlink.text = '<-Back';
	backdiv.appendChild(backlink);
	container.appendChild(backdiv);

	const scorewrapper = document.createElement('div');
	scorewrapper.className = "scorewrapperdiv";

	scorewrapper.appendChild(buildScorecardTable(pairnum));

	const boarddiv = document.createElement('div');
	boarddiv.className = "boarddiv";
	boarddiv.id = "boardcontent"
	scorewrapper.appendChild(boarddiv);

	container.appendChild(scorewrapper);

	// Create second back link
	const backdiv2 = document.createElement('div');
	backdiv2.className = "backlink";
	const backlink2 = document.createElement('a');
	backlink2.href = '#';
	backlink2.onclick = function(event) { event.preventDefault(); renderContent() };
	backlink2.text = '<-Back';
	backdiv2.appendChild(backlink2);
	container.appendChild(backdiv2);
}

/*************************************************************************/
function boardClick(boardNum, pairnum) {
	// Clear out the container first
	const container = document.getElementById('boardcontent');
	container.innerHTML = ''; // Clear previous content

	const boarddiv = document.createElement('div');
	boarddiv.className = "oneboarddiv";
	boarddiv.appendChild(buildDeal(boardNum));

	const travdiv = document.createElement('div');
	travdiv.className = "onetravdiv";
	travdiv.appendChild(buildTraveller(boardNum, pairnum));
	container.appendChild(boarddiv);
	container.appendChild(travdiv);

	const btnspacediv = document.createElement('div');
	btnspacediv.className = "btnwrapper";

	if (boardNum < eventInfo.numboards) {
		const fwdbddiv = document.createElement('div');
		fwdbddiv.className = "bdlinkfwd";
		const fwdlink = document.createElement('a');
		fwdlink.href = '#';
		fwdlink.onclick = function(event) { event.preventDefault(); boardClick(boardNum + 1, pairnum) };
		fwdlink.text = 'Next->   ';
		fwdbddiv.appendChild(fwdlink);
		btnspacediv.appendChild(fwdbddiv);
	}
	if (boardNum > 1) {
		const backbddiv = document.createElement('div');
		backbddiv.className = "bdlinkbck";
		const backlink = document.createElement('a');
		backlink.href = '#';
		backlink.onclick = function(event) { event.preventDefault(); boardClick(boardNum - 1, pairnum) };
		backlink.text = '   <-Prev';
		backbddiv.appendChild(backlink);
		btnspacediv.appendChild(backbddiv);
	}
	container.appendChild(btnspacediv);
}

/*************************************************************************/
function getPairName(pairnum) {
	var pairname;
	rankings.data.forEach(rankingRecord => {
		if (rankingRecord.pairnum == pairnum) {
			pairname = rankingRecord.pair;
		}
	});
	if (pairname == null && typeof rankingsew !== 'undefined') {
		rankingsew.data.forEach(rankingRecord => {
			if (rankingRecord.pairnum == pairnum) {
				pairname = rankingRecord.pair;
			}
		});
	}
	return pairname;
}
