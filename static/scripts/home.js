alert('hey')
// UI Class
class UI {
    // showAlert
    static showAlert(alertText, type, position) {
        if (type === undefined || !(['primary', 'warning', 'danger', 'success'].includes(type))) {
            type = 'primary'
        }
        if (position === undefined || !(['top', 'aboveTable'].includes(position))) {
            position = 'top'
        }
        // Create alert div
        const alertDiv = document.createElement('div')
        alertDiv.role = 'alert'
        alertDiv.className = `alert alert-${type}`
        alertDiv.id = 'alertMessage'
        alertDiv.style.borderRadius = '10px'
        alertDiv.textContent = alertText
        // Adjust style
        if (type === 'danger') {
            alertDiv.style.backgroundColor = 'rgb(209,13,13)'
        }
        if (type === 'primary') {
            alertDiv.style.backgroundColor = 'rgb(80, 113, 213)'
        }
        if (type === 'success') {
            alertDiv.style.backgroundColor = 'rgb(76, 180, 40)'
        }
        if (type === 'warning') {
            alertDiv.style.backgroundColor = 'rgb(227, 148, 16)'
        }
        // Adjust position
        if (position === 'top') {
            // Add alert to page
            document.querySelector('.alert-container-top').appendChild(alertDiv)
        }
        if (position === 'aboveTable') {
            // Add alert to page
            document.querySelector('.alert-container-above-table').appendChild(alertDiv)
        }

        // Remove alert
        setTimeout(()=>{alertDiv.remove()}, 3000)

    }
    // populateTable
    static populateTable(timePeriod, sortBy, order) {
        // Clear the table
        this.removeAllChildNodes(document.getElementById('tableBody'))

        // Initialize new request
        const request = new XMLHttpRequest();
        request.open('GET', `/getExpenses/${timePeriod}/${sortBy}/${order}`);

        // Callback function for when request completes
        request.onload = () => {
            // Extract JSON data from request
            const data = JSON.parse(request.responseText);
            if (data.length === 0) {
                document.querySelector('#mainTable').style.display = "none"
            }
            else {
                document.querySelector('#mainTable').style.display = ""
            }

            // CREATE TABLE DATA
            var tableBody = document.getElementById('tableBody')

            for (let i = 0; i < data.length; i ++) {
                let tr = document.createElement('tr')

                // NAME DATA
                let tdName = document.createElement('td')
                tdName.className = "table_data"
                tdName.height = "65px"
                // tdName.width = "10px"
                let itemNameText = data[i]['item_name']
                tdName.textContent = itemNameText

                // PRICE DATA
                let tdPrice = document.createElement('td')
                tdPrice.className = "table_data"
                let itemPriceText = '$' + data[i]['item_price']
                tdPrice.textContent = itemPriceText

                // DATE DATA
                let tdDate = document.createElement('td')
                tdDate.className = "table_data"
                let itemDateText = data[i]['date']
                tdDate.textContent = itemDateText

                // TIME DATA
                let tdTime = document.createElement('td')
                tdTime.className = "table_data"
                let itemTimeText = data[i]['time']
                tdTime.textContent = itemTimeText

                // ACTIONS BUTTON
                let tdButton  = document.createElement('td')

                // EDIT BUTTON
                let editBtn = document.createElement('a')
                editBtn.href = "#editExpenseModal"
                editBtn.className = "edit"
                editBtn.dataset.toggle="modal"
                // ICON
                let editIcon = document.createElement('i')
                editIcon.className = "material-icons"
                editIcon.dataset.toggle = "tooltip"
                editIcon.dataset.item_id = data[i]['id']
                editIcon.title = "Edit"
                editIcon.innerHTML = "&#xE254;"

                editBtn.appendChild(editIcon)
                tdButton.appendChild(editBtn)

                // DELETE BTN
                let deleteBtn = document.createElement('a')
                deleteBtn.href = "#deleteExpenseModal"
                deleteBtn.className = "delete"
                deleteBtn.dataset.toggle = "modal"
                // ICON
                let deleteIcon = document.createElement('i')
                deleteIcon.className = "material-icons"
                deleteIcon.dataset.toggle = "tooltip"
                deleteIcon.dataset.item_id = data[i]['id']
                deleteIcon.title = "Delete"
                deleteIcon.innerHTML = "&#xE872;"

                deleteBtn.appendChild(deleteIcon)
                tdButton.appendChild(deleteBtn)


                tr.appendChild(tdName)
                tr.appendChild(tdPrice)
                tr.appendChild(tdDate)
                tr.appendChild(tdTime)
                tr.appendChild(tdButton)

                tableBody.appendChild(tr)

            }

            // LAST ROW
            let extraTr = document.createElement('tr')
            extraTr.className = "table-active"

            let averageExpenseTdHeading = document.createElement('td')
            averageExpenseTdHeading.id = "averageExpenseHeading"
            averageExpenseTdHeading.style.fontWeight = "bold"
            averageExpenseTdHeading.textContent = "Average Expense"

            // EMPLY TD SLOTS
            // let emptyTd1 = document.createElement('td')
            // let emptyTd2 = document.createElement('td')

            // AVERAGE EXPENSE
            let averageExpenseTd = document.createElement('td')
            averageExpenseTd.className = "table_data"
            if (data.length !== 0)
                averageExpenseTd.textContent = "$" + Expense.computeAverageExpense(data).toFixed(2)
            else
                averageExpenseTd.textContent = ""

            extraTr.appendChild(averageExpenseTdHeading)
            // extraTr.appendChild(emptyTd1)
            // extraTr.appendChild(emptyTd2)
            extraTr.appendChild(averageExpenseTd)

            tableBody.appendChild(extraTr)

        }
        request.send(200);

    }
    // UPDATE EXPENSE TABLE HEADINGS
    static updateExpenseTableHeadings(timePeriod, sortBy, order) {
        let expenseTableHeading = document.querySelector('#expenseTableHeading')
        let expenseTableSelectTimePeriod = document.querySelector('#expenseTableSelectTimePeriod')
        let expenseTableSort = document.querySelector('#expenseTableSort')

        let expenseTableSelectTimePeriodOptions =  generateSelectOptionsDict(expenseTableSelectTimePeriod)

        // Time Period
        switch (timePeriod) {
            case 'this-day':
                expenseTableHeading.textContent = 'Expenses For Today'
                expenseTableSelectTimePeriodOptions['this-day'].selected = true
                break
            case 'this-week':
                expenseTableHeading.textContent = 'Expenses For This Week'
                expenseTableSelectTimePeriodOptions['this-week'].selected = true
                break
            case 'this-month':
                expenseTableHeading.textContent = 'Expenses For This Month'
                expenseTableSelectTimePeriodOptions['this-month'].selected = true
                break
            case 'this-year':
                expenseTableHeading.textContent = 'Expenses For This Year'
                expenseTableSelectTimePeriodOptions['this-year'].selected = true
                break
            case 'all-time':
                expenseTableHeading.textContent = 'All Time Expenses'
                expenseTableSelectTimePeriodOptions['all-time'].selected = true
                break
        }
        // SortBy
        switch (sortBy) {
            case 'item_name':
                if (order === 'asc')
                    expenseTableSort.options[0].selected = true
                else
                    expenseTableSort.options[1].selected = true
                break
            case 'item_price':
                if (order === 'asc')
                    expenseTableSort.options[2].selected = true
                else
                    expenseTableSort.options[3].selected = true
                break

        }
    }
    // removeAllChildNodes
    static removeAllChildNodes(parent) {
        while (parent.firstChild) {
            parent.removeChild(parent.firstChild)
        }
    }
    // SCROLL TO TOP
    static scrollToTop() {
        window.scrollTo({ top: 0, behavior: 'smooth' })
    }
    // DISABLE SCROLL
    static disableScroll() {
        // Get the current page scroll position
        let scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        let scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;

        // if any scroll is attempted, set this to the previous value
        window.onscroll = function() {
            window.scrollTo(scrollLeft, scrollTop);
        };
    }
    // ENABLE SCROLL
    static enableScroll() {
        window.onscroll = function() {};
    }

}
// Expense Class
class Expense {
    // ADD EXPENSE
    static addExpense() {
        let expenseName = document.forms["addExpenseForm"]["expenseName"]
        let expensePrice =  document.forms["addExpenseForm"]["expensePrice"]
        let exceedLimitText = document.querySelector('#exceedLimitText')

        let addExpenseBtn = document.querySelector('#addExpenseBtn')
        let expenseData = {
            'expenseName': expenseName.value,
            'expensePrice': expensePrice.value,
            'auto-send-email': localStorage.getItem('auto-send-email')
        }

        let sortBy = document.querySelector('#expenseTableSort').value
        let order = document.querySelector('#expenseTableSort').selectedOptions[0].dataset.order


        const request = new XMLHttpRequest()
        request.open('POST', `/addExpense/${JSON.stringify(expenseData)}`)
        request.onload = () => {
            addExpenseBtn.disabled = true
            UI.scrollToTop()
            UI.populateTable(document.querySelector('#expenseTableSelectTimePeriod').value, sortBy, order)
            UI.showAlert(`${expenseName.value} Has Been Added`, 'success', 'top')
            expenseName.value = ""
            expensePrice.value = ""
            exceedLimitText.textContent = ""
        }
        request.send()

    }
    // ADD EXPENSE LIMIT
    static setExpenseLimit(timePeriod, expenseLimitSetText, expenseLimitInput) {
        const request = new XMLHttpRequest()
        request.open('POST', `/setExpenseLimit/${expenseLimitInput.value}/${timePeriod}`)
        request.send()

        let periodToDisplay
        if (timePeriod === 'this-day') {
            periodToDisplay = "Today"
        }
        else if (timePeriod === 'this-week') {
            periodToDisplay = "This Week"
        }
        else if (timePeriod === 'this-month') {
            periodToDisplay = "This Month"
        }
        else if (timePeriod === 'this-year') {
            periodToDisplay = "This Year"
        }
        expenseLimitSetText.textContent = `Expense Limit Set To $${expenseLimitInput.value} For ${periodToDisplay}`
        document.querySelector('#expenseLimitLabel').textContent = `Spending Limit: $${expenseLimitInput.value}`
        expenseLimitInput.value = ""
        setTimeout(() => {expenseLimitSetText.textContent = ""}, 3000)
        setTimeout(() => {document.querySelector('#setExpenseLimitCancelBtn').click()}, 3000)

    }
    // VALIDATE ADD EXPENSE FORM
    static validateAddExpenseForm() {
        var expenseNameField = document.forms["addExpenseForm"]["expenseName"].value
        var expensePriceField = document.forms["addExpenseForm"]["expensePrice"].value
        var addExpenseBtn = document.querySelector('#addExpenseBtn')
        var exceedLimitText = document.getElementById('exceedLimitText')

        if (expenseNameField !== '' && expensePriceField !== '') {
            addExpenseBtn.disabled = false
        }
        else {
            addExpenseBtn.disabled = true
        }

        if (expensePriceField !== '') {
            if (isNaN(expensePriceField)) {
                if (expensePriceField.includes('$')) {
                    exceedLimitText.style.color = "orange"
                    exceedLimitText.textContent = "Enter the price without the use of '$'"
                }
                document.querySelector('#itemPrice').style.borderColor = "red"
                addExpenseBtn.disabled = true
            }
            else {
                document.querySelector('#itemPrice').style.borderColor = ""
            }
        }
        else {
            document.querySelector('#itemPrice').style.borderColor = ""
        }

    }
    // EXPENSE TO BE ADDED WILL EXCEED LIMIT
    static expenseToBeAddedWillExceedLimit() {
        var expensePriceField = document.forms["addExpenseForm"]["expensePrice"].value

        var dayLimit = Expense.getUserExpenseLimit('this-day')
        var weekLimit = Expense.getUserExpenseLimit('this-week')
        var monthLimit = Expense.getUserExpenseLimit('this-month')
        var yearLimit = Expense.getUserExpenseLimit('this-year')

        var totalDay = parseFloat(Expense.getTotalUserExpenses('this-day'))
        var totalWeek = parseFloat(Expense.getTotalUserExpenses('this-week'))
        var totalMonth = parseFloat(Expense.getTotalUserExpenses('this-month'))
        var totalYear = parseFloat(Expense.getTotalUserExpenses('this-year'))

        var exceedLimitText = document.getElementById('exceedLimitText')

        // CHECK IF THE EXPENSE THAT IS ABOUT TO BE ADDED WILL EXCEED THE EXPENSE LIMIT SET
        let over = false
        if ((totalDay + parseFloat(expensePriceField)) > dayLimit && dayLimit != null) {
            over = true
            exceedLimitText.style.color = "red"
            exceedLimitText.textContent = "This expense will go over your limit for the day"
        }
        if ((totalWeek + parseFloat(expensePriceField)) > weekLimit && weekLimit != null) {
            over = true
            exceedLimitText.style.color = "red"
            exceedLimitText.textContent = "This expense will go over your limit for the week"
        }
        if ((totalMonth + parseFloat(expensePriceField)) > monthLimit && monthLimit != null) {
            over = true
            exceedLimitText.style.color = "red"
            exceedLimitText.textContent = "This expense will go over your limit for the month"
        }
        if ((totalYear + parseFloat(expensePriceField)) > yearLimit && yearLimit != null) {
            over = true
            exceedLimitText.style.color = "red"
            exceedLimitText.textContent = "This expense will go over your limit for the year"
        }
        if (over === false) {
            exceedLimitText.textContent = ""
        }

    }
    // DISPLAY TOTAL EXPENSE
    static displayTotalExpense(period) {
        let totalExpenseLabel = document.getElementById('totalExpenseLabel')

        // Initialize new request
        const request = new XMLHttpRequest()
        request.open('GET', `/getTotalExpense/${period}`)

        // Callback function for when request completes
        request.onload = () => {
            var totalExpense = parseFloat(request.responseText)
            totalExpenseLabel.textContent = "Total Expense: $" + totalExpense.toFixed(2)
        }
        request.send()
    }
    // DISPLAY EXPENSE LIMIT
    static displayExpenseLimit(period) {
        const request = new XMLHttpRequest()
        request.open('GET', `/getExpenseLimit/${period}`)

        request.onload = () => {
            const data = parseFloat(request.responseText)
            if (isNaN(data)) {
                document.querySelector('#expenseLimitLabel').textContent = `Spending Limit: Not Set`
            }
            else {
                document.querySelector('#expenseLimitLabel').textContent = `Spending Limit: $${data.toFixed(2)}`
            }

        }
        request.send()
    }
    // GET USER EXPENSE LIMIT
    static getUserExpenseLimit(period) {
        this.loadUserExpenseLimits()
        let userExpenseLimits = JSON.parse(document.querySelector('#userExpenseLimits').dataset.user_expense_limits)
        return userExpenseLimits[period]
    }
    // GET TOTAL USER EXPENSES
    static getTotalUserExpenses(period) {
        this.loadTotalUserExpenses()
        let totalExpenses = JSON.parse(document.querySelector('#totalUserExpenses').dataset.total_user_expenses)
        return totalExpenses[period]
    }
    // LOAD USER EXPENSE LIMITS
    static loadUserExpenseLimits() {
        const request = new XMLHttpRequest()
        request.open('GET', '/getExpenseLimit/all-limits-json')
        request.onload = () => {
            const data = JSON.stringify(JSON.parse(request.responseText))
            document.querySelector('#userExpenseLimits').dataset.user_expense_limits = data
        }
        request.send()
    }
    // LOAD TOTAL USER EXPENSES
    static loadTotalUserExpenses() {
        const request = new XMLHttpRequest()
        request.open('GET', '/getTotalExpense/all-expenses-JSON')
        request.onload = () => {
            const data = JSON.stringify(JSON.parse(request.responseText))
            document.querySelector('#totalUserExpenses').dataset.total_user_expenses = data
        }
        request.send()
    }
    // UPDATE EXPENSE TABLE BASED ON PERIOD
    static updateExpenseTableBasedOnPeriod() {
        let tableHeading
        let timePeriod = document.querySelector('#expenseTableSelectTimePeriod').value
        let sortBy = document.querySelector('#expenseTableSort').value
        let order = document.querySelector('#expenseTableSort').selectedOptions[0].dataset.order
        if (timePeriod === 'all-time') {
            tableHeading = 'All Time Expenses'
        }
        else if (timePeriod === 'this-day') {
            tableHeading = 'Expenses For Today'
        }
        else if (timePeriod === 'this-week') {
            tableHeading = 'Expenses For This Week'
        }
        else if (timePeriod === 'this-month') {
            tableHeading = 'Expenses For This Month'
        }
        else if (timePeriod === 'this-year') {
            tableHeading = 'Expenses For This Year'
        }

        let tableBody = document.getElementById('tableBody')
        let expenseTableHeading = document.getElementById('expenseTableHeading')
        expenseTableHeading.textContent = tableHeading
        // REMOVE PREVIOUS DATA FROM TABLE TO POPULATE IT WITH NEW ONE DATA
        UI.removeAllChildNodes(tableBody)
        Settings.updateUserSettings('expenseTable-Time-Period', timePeriod)
        UI.populateTable(timePeriod, sortBy, order)
    }
    // SORT EXPENSE TABLE
    static sortExpenseTable() {
        let expenseTableSelectSort = document.querySelector('#expenseTableSort')

        let timePeriod = document.querySelector('#expenseTableSelectTimePeriod').value
        let sortBy = expenseTableSelectSort.value
        let order = expenseTableSelectSort.selectedOptions[0].dataset.order


        Settings.updateUserSettings('expenseTable-SortBy', sortBy)
        Settings.updateUserSettings('expenseTable-Order', order)
        UI.populateTable(timePeriod, sortBy, order)


    }
    // EDIT EXPENSE MODAL
    static showEditExpenseModal(itemID, sortBy, order) {
        // VALIDATE EDIT MODAL FORM
        var saveEditBtn = document.querySelector('#saveEditBtn')
        document.querySelector('#editExpenseForm').onkeyup = () => {
            let newNameField = document.forms["editExpenseForm"]["newName"].value
            let newPriceField = document.forms["editExpenseForm"]["newPrice"]

            let errorMessage = document.querySelector('#errorMessage')
            // INPUT FIELDS EMPTY
            if (newNameField === "" && newPriceField.value === "") {
                saveEditBtn.disabled = true
            }
            else {
                saveEditBtn.disabled = false
            }
            // PRICE FIELD NOT A NUMBER
            if (isNaN(newPriceField.value)) {
                if (newPriceField.value.includes('$')) {
                    errorMessage.textContent = "Enter the price without the use of '$'"
                }
                else {
                    errorMessage.textContent = ""
                    newPriceField.style.borderColor = ""
                }
                newPriceField.style.borderColor = "orange"
                saveEditBtn.disabled = true
            }
            else {
                newPriceField.style.borderColor = ""
                errorMessage.textContent = ""
            }
            if (newPriceField.value === "") {
                newPriceField.style.borderColor = ""
                errorMessage.textContent = ""
            }
        }
        // SUBMIT FORM
        saveEditBtn.onclick = () => {
            let newNameField = document.forms["editExpenseForm"]["newName"].value
            let newPriceField = document.forms["editExpenseForm"]["newPrice"].value
            if (newPriceField === "") {
                newPriceField = "Empty"
            }
            if (newNameField === "") {
                newNameField = "Empty"
            }

            const request = new XMLHttpRequest()
            request.open('POST', `/editExpense/${itemID}/${newNameField}/${newPriceField}`)
            request.onload = () => {
                let tableBody = document.getElementById('tableBody')
                let timePeriod = document.querySelector('#expenseTableSelectTimePeriod').value
                // UPDATE UI
                document.forms["editExpenseForm"]["newName"].value = ""
                document.forms["editExpenseForm"]["newPrice"].value = ""
                Expense.removeEditExpenseModal()
                UI.showAlert("Expense Changed", 'primary', 'aboveTable')
                UI.removeAllChildNodes(tableBody)
                Expense.displayTotalExpense(timePeriod)
                UI.populateTable(timePeriod, sortBy, order)
            }
            request.send()
        }

    }
    // DELETE EXPENSE  MODAL
    static showDeleteExpenseModal(itemID, sortBy, order) {
        document.querySelector('#deleteExpenseBtn').onclick = () => {
            const request = new XMLHttpRequest()
            request.open('POST', `/deleteExpense/${itemID}`)
            request.onload = () => {
                let tableBody = document.getElementById('tableBody')
                let timePeriod = document.querySelector('#expenseTableSelectTimePeriod').value
                Expense.removeDeleteExpenseModal()
                UI.showAlert("Expense Deleted", 'danger', 'aboveTable')
                UI.removeAllChildNodes(tableBody)
                Expense.displayTotalExpense(timePeriod)
                UI.populateTable(timePeriod, sortBy, order)
            }
            request.send()
        }

    }
    // AVERAGE EXPENSE
    static computeAverageExpense(data) {
        let totalExpense = 0
        for (let i = 0; i < data.length; i ++) {
            totalExpense += data[i]['item_price']
        }
        let average = totalExpense / data.length
        return average
    }
    //  REMOVE MODALS
    static removeEditExpenseModal() {
        document.querySelector('#editModalCancelBtn').click()
    }
    static removeDeleteExpenseModal() {
        document.querySelector('#deleteExpenseCancelBtn').click()
    }

}
// ScheduleExpense Class
class ScheduleExpense {
    // UPDATE FREQUENCY
    static updateFrequencySelect(period) {
        let frequencySelect = document.querySelector('#frequencySelect')
        switch (period) {
            case 'day':
                frequencySelect.innerHTML = `
                <option value="every-day">Every Day</option>
                <option value="2-days">Every 2 Days</option>
                <option value="3-days">Every 3 Days</option>
                <option value="custom-day">Custom</option>
                `
                break
            case 'week':
                frequencySelect.innerHTML = `
                <option value="every-week">Every Week</option>
                <option value="2-weeks">Every 2 Weeks</option>
                <option value="3-weeks">Every 3 Weeks</option>
                <option value="custom-week">Custom</option>
                `
                break
            case 'month':
                frequencySelect.innerHTML = `
                <option value="every-week">Every Month</option>
                <option value="2-months">Every 2 Months</option>
                <option value="3-months">Every 3 Months</option>
                <option value="custom-month">Custom</option>
                `
                break
            case 'year':
                frequencySelect.innerHTML = `
                <option value="every-week">Every Year</option>
                <option value="2-years">Every 2 Years</option>
                <option value="3-years">Every 3 Years</option>
                <option value="custom-year">Custom</option>
                `
                break
        }

    }
    // SHOW CUSTOM FREQUENCY
    static showCustomFrequency() {
        document.querySelector('#customFrequencyHeading').style.display = 'block'
        document.querySelector('#customFrequencyInput').style.display = 'block'

    }
    // REMOVE CUSTOM FREQUENCY
    static removeCustomFrequency() {
        document.querySelector('#customFrequencyHeading').style.display = 'none'
        document.querySelector('#customFrequencyInput').style.display = 'none'

    }


}
// Settings Class
class Settings {
    /** PRIVATE METHODS **/

    // Get All Setting Keys
    static #getAllSettingKeys() {
        let allKeys = []
        for (let key in this.getUserSettings()) {
            allKeys.push(key)
        }
        return allKeys
    }
    // Check if Setting Value is Valid
    static #isValidSettingValue(settingToUpdate, newValue) {
        if (settingToUpdate === 'expenseTable-Time-Period') {
            let allValidTimePeriods = ['this-day', 'this-week', 'this-month', 'this-year', 'all-time']
            if (!(allValidTimePeriods).includes(newValue)) {
                return false
            }
        }
        if (settingToUpdate === 'expenseTable-SortBy') {
            let allValidSortBy = ['item_name', 'item_price']
            if (!(allValidSortBy.includes(newValue))) {
                return false
            }
        }
        if (settingToUpdate === 'expenseTable-Order') {
            let allValidOrders = ['asc', 'desc']
            if (!(allValidOrders.includes(newValue))) {
                return false
            }
        }

        return true
    }

    // INITIALIZE USER SETTINGS
    static initializeUserSettings() {
        if (!(localStorage.getItem('Budgit-userSettings'))) {
            localStorage.setItem('Budgit-userSettings', JSON.stringify({
                'expenseTable-Time-Period': 'this-day',
                'expenseTable-SortBy': 'item_name',
                'expenseTable-Order': 'asc',
            }))
        }
    }
    // GET USER SETTINGS
    static getUserSettings() {
        this.initializeUserSettings()
        return JSON.parse(localStorage.getItem('Budgit-userSettings'))
    }
    // UPDATE USER SETTINGS
    static updateUserSettings(settingToUpdate, newValue) {
        // Invalid settingToUpdate
        if (!(this.#getAllSettingKeys().includes(settingToUpdate))) {
            throw `Exception: updateUserSetting(${settingToUpdate}, ${newValue}). '${settingToUpdate}' is not a valid setting to update.`
        }
        // Invalid neValue
        if (!(this.#isValidSettingValue(settingToUpdate, newValue))) {
            throw `Exception: updateUserSetting(${settingToUpdate}, ${newValue}). '${newValue}' is not a valid setting for ${settingToUpdate}.`

        }
        // Get the settings from storage
        let S = this.getUserSettings()
        // Update the setting
        S[settingToUpdate] = newValue
        // Push the new settings back to storage
        localStorage.setItem('Budgit-userSettings', JSON.stringify(S))
    }


}
//
//
// // DOM CONTENT LOADED
// document.addEventListener('DOMContentLoaded', () => {
//     Settings.initializeUserSettings()
//     let userSettings = {
//         'timePeriod': Settings.getUserSettings()['expenseTable-Time-Period'],
//         'sortBy': Settings.getUserSettings()['expenseTable-SortBy'],
//         'order': Settings.getUserSettings()['expenseTable-Order'],
//     }
//
//
//     UI.populateTable(userSettings['timePeriod'], userSettings['sortBy'] , userSettings['order'])
//     UI.updateExpenseTableHeadings(userSettings['timePeriod'], userSettings['sortBy'] , userSettings['order'])
//     Expense.loadTotalUserExpenses()
//     Expense.loadUserExpenseLimits()
//     Expense.displayTotalExpense(userSettings['timePeriod'])
//     Expense.displayExpenseLimit(userSettings['timePeriod'])
// })
//
//
// /** ON-CLICK EVENTS **/
//
// // Add Expense
// document.querySelector('#addExpenseBtn').onclick = function() {Expense.addExpense()}
// // Expense Table Buttons
// document.querySelector('#mainTable').addEventListener('click', (e) =>{
//     var itemID = e.target.dataset.item_id
//     let sortBy = document.querySelector('#expenseTableSort').value
//     let order = document.querySelector('#expenseTableSort').selectedOptions[0].dataset.order
//
//     // EDIT BUTTON
//     if (e.target.className === "material-icons" && e.target.title === "Edit") {
//         Expense.showEditExpenseModal(itemID, sortBy, order)
//     }
//     // DELETE BUTTON
//     else if (e.target.className === "material-icons" && e.target.title === "Delete") {
//         Expense.showDeleteExpenseModal(itemID, sortBy, order)
//     }
//
// })
// // Set The Expense Limit
// document.querySelector('#setLimitBtn').onclick = () => {
//     let timePeriod = document.querySelector('#expenseLimitModalSelect').value
//     let expenseLimitSetText = document.querySelector('#expenseLimitSetText')
//     let expenseLimitInput = document.forms["limitForm"]["expenseLimit"]
//
//     Expense.setExpenseLimit(timePeriod, expenseLimitSetText, expenseLimitInput)
// }
// // Change Frequency Select Depending On The Time Period
// document.querySelector('.time-period-container').onclick = (e) => {
//     if (e.target.className === 'form-check-input') {
//         document.querySelector('#customFrequencyInput').value = ''
//         ScheduleExpense.updateFrequencySelect(e.target.value)
//         ScheduleExpense.removeCustomFrequency()
//     }
// }
//
//
// /** ON-CHANGE EVENTS **/
//
// // Expense Table Select -> Period
// document.querySelector('#expenseTableSelectTimePeriod').onchange = () => {Expense.updateExpenseTableBasedOnPeriod()}
// // Expense Table Select -> Sort
// document.querySelector('#expenseTableSort').onchange = () => {Expense.sortExpenseTable()}
// // Update Expense Limit Modal Heading
// document.querySelector('#expenseLimitModalSelect').onchange = function() {
//     let expenseLimitModalHeading = document.querySelector('#expenseLimitModalHeading')
//     if (this.value === 'this-day') {
//         expenseLimitModalHeading.textContent = "Set Expense Limit For Today"
//     }
//     else if (this.value === 'this-week') {
//         expenseLimitModalHeading.textContent = "Set Expense Limit For This Week"
//     }
//     else if (this.value === 'this-month') {
//         expenseLimitModalHeading.textContent = "Set Expense Limit For This Month"
//     }
//     else if (this.value === 'this-year') {
//         expenseLimitModalHeading.textContent = "Set Expense Limit For This Year"
//     }
// }
// // Total Expense Select
// document.querySelector('#totalExpenseSelect').onchange = function() {
//     var timePeriod = this.value
//     Expense.displayTotalExpense(timePeriod)
// }
// // Expense Limit Select
// document.querySelector('#expenseLimitSelect').onchange = function() {Expense.displayExpenseLimit(this.value)}
// // Schedule Expense Frequency Select -> 'custom' Has Been Selected
// document.querySelector('#frequencySelect').onchange = function() {
//     let customFrequencyHeading = document.querySelector('#customFrequencyHeading')
//     let customFrequencyInput = document.querySelector('#customFrequencyInput')
//     switch (this.value) {
//         case 'custom-day':
//             customFrequencyHeading.textContent = 'Custom Day'
//             ScheduleExpense.showCustomFrequency()
//             break
//         case 'custom-week':
//             customFrequencyHeading.textContent = 'Custom Week'
//             ScheduleExpense.showCustomFrequency()
//             break
//         case 'custom-month':
//             customFrequencyHeading.textContent = 'Custom Month'
//             ScheduleExpense.showCustomFrequency()
//             break
//         case 'custom-year':
//             customFrequencyHeading.textContent = 'Custom Year'
//             ScheduleExpense.showCustomFrequency()
//             break
//         default:
//             ScheduleExpense.removeCustomFrequency()
//     }
// }
//
//
// /** ON-KEY UP EVENTS **/
//
// // Validate Set Expense Limit Input
// document.querySelector('#limitForm').onkeyup = () => {
//     let expenseLimit = document.forms["limitForm"]["expenseLimit"].value
//     let setLimitBtn = document.getElementById("setLimitBtn")
//
//     if (expenseLimit === '' || isNaN(expenseLimit))
//         setLimitBtn.disabled = true
//     else
//         setLimitBtn.disabled = false
// }
// // Validate Add Expense Form
// document.querySelector('#addExpenseForm').onkeyup = () => {Expense.validateAddExpenseForm()}
// // Check If Expense That Is About To Be Added Will Exceed a Limit
// document.querySelector('#itemPrice').onkeyup = () => {Expense.expenseToBeAddedWillExceedLimit()}
//
//
// /** ON-BLUR EVENTS **/
//
// // Custom Frequency Input
// document.querySelector('#customFrequencyInput').onblur = function() {
//     let customFrequencyHeading = document.querySelector('#customFrequencyHeading')
//     let headingToUse = ''
//
//     // Extract the first two words for the heading
//     let arrayOfHeading = customFrequencyHeading.textContent.split(' ')
//     for (let i = 0; i < 2; i++) {
//         headingToUse += arrayOfHeading[i]
//         headingToUse += ' '
//     }
//     headingToUse = headingToUse.trimEnd()
//     let period = headingToUse.split(' ')[1]
//
//
//     if (this.value !== '') {
//         customFrequencyHeading.innerHTML = `${headingToUse} → <span style="font-weight: normal">Every ${this.value} ${period}s</span>`
//     }
//     else {
//         customFrequencyHeading.textContent = headingToUse
//     }
// }
//
//
// /**
//  * Generates an object created from a <select> html element. The key is the value of a specific option in the select
//  * and the value is the select itself
//  * @param {Node} SelectNode Delimited sequence of names.
//  * @return {Object}
//  */
// function generateSelectOptionsDict(SelectNode) {
//     let allOptions = SelectNode.options
//     let selectOptionsDict = {}
//
//     for (option of allOptions) {
//         selectOptionsDict[option.value] = option
//     }
//     return selectOptionsDict
//
//
//
// }