const convertButton = document.getElementById('cbtn');
const downloadButton = document.getElementById('dbtn');
const summaryView = document.getElementById('s-summary');
const fileInput = document.getElementById('inputGroupFile03');
const spinner = document.getElementById('l-spinner');

// Variables
let multiSummary;
let finalSummary;
let selectedFile;
const maxFileSize = (1024) * 150; // 150KB

/**
 * On Change event listener for the input
 */

fileInput.addEventListener('change', (event) => {
    
    const file = event.target.files[0];
    selectedFile = file;

    if (file) {
        console.log(file.size, "-", maxFileSize);
        if (file.size > maxFileSize) {
            alert("File is too big. Maximum file size allowed is 150KB.");
            fileInput.value = ""; // clear the selected file
            return;
        }
        convertButton.removeAttribute('disabled');
        downloadButton.classList.add('d-none');
        summaryView.innerHTML = ''
    }
});

// Click event to download files
downloadButton.addEventListener('click', ()=>{
   

    let multiSumaryBlob = new Blob([multiSummary], { type : 'plain/text' });
    let mergedSummarySumaryBlob = new Blob([finalSummary], { type : 'plain/text' });
    const multiUrl = window.URL.createObjectURL(multiSumaryBlob);
    const mergedUrl = window.URL.createObjectURL(mergedSummarySumaryBlob);

    const downloadLink1 = document.createElement('a');
    const downloadLink2 = document.createElement('a');
    downloadLink1.href = multiUrl;
    downloadLink2.href = mergedUrl;
    downloadLink1.download = "multi_summary.txt";
    downloadLink2.download = "merged_summary.txt";

    downloadLink1.click();
    downloadLink2.click();
})

// Click event to convert pdf screenplay
convertButton.addEventListener('click', ()=>{

    /** Set button spinner, and disable button */
    spinner.classList.remove('d-none');
    convertButton.setAttribute('disabled', '');

    /** Send POST request */
    const form = new FormData();
    console.log(selectedFile);
    form.append('file', selectedFile);

    const xhr = new XMLHttpRequest();
    xhr.open('POST', `/api/summarize`); 
    xhr.send(form);
    
    // Set up load event listener
    xhr.onload = () => {

        if (xhr.status === 200) {

            /** Stop loading spinner and disable button */
            spinner.classList.add('d-none');

            // Store response
            let parsedResponse = JSON.parse(xhr.responseText);
            multiSummary = parsedResponse.multi_summary;
            finalSummary = parsedResponse.merged_summary;


            // Display summary
            summaryView.append(finalSummary);

            // Allow user to download files
            downloadButton.classList.remove('d-none');

        }
        else{
            xhr.responseType = 'string';
            spinner.classList.add('d-none');
            const response = JSON.parse(xhr.responseText);
            window.alert(response.message);
            convertButton.removeAttribute('disabled');
        }
    };
})
