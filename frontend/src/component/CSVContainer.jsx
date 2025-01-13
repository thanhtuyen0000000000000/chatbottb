import { useState } from 'react';
import PropTypes from 'prop-types';

// Helper function to generate pagination buttons
function getPaginationButtons(currentPage, totalPages) {
  const maxVisibleButtons = 5;
  const buttons = [];
  const half = Math.floor(maxVisibleButtons / 2);

  if (totalPages <= maxVisibleButtons) {
    for (let i = 1; i <= totalPages; i++) {
      buttons.push(i);
    }
  } else {
    if (currentPage <= half + 1) {
      for (let i = 1; i <= maxVisibleButtons; i++) {
        buttons.push(i);
      }
      buttons.push('...');
      buttons.push(totalPages);
    } else if (currentPage > totalPages - half) {
      buttons.push(1);
      buttons.push('...');
      for (let i = totalPages - maxVisibleButtons + 1; i <= totalPages; i++) {
        buttons.push(i);
      }
    } else {
      buttons.push(1);
      buttons.push('...');
      for (let i = currentPage - half; i <= currentPage + half; i++) {
        buttons.push(i);
      }
      buttons.push('...');
      buttons.push(totalPages);
    }
  }

  return buttons;
}

function CSVContainer({ csvData, onFileUpload, rowsPerPage }) {
  const [currentPage, setCurrentPage] = useState(1);

  const totalPages = Math.ceil((csvData.length - 1) / rowsPerPage); // Skip the header row

  const paginate = (pageNumber) => {
    if (pageNumber >= 1 && pageNumber <= totalPages) {
      setCurrentPage(pageNumber);
    }
  };

  const currentTableData = () => {
    const startIndex = (currentPage - 1) * rowsPerPage + 1; // Start from row after the header
    const endIndex = startIndex + rowsPerPage;
    return csvData.slice(startIndex, endIndex);
  };

  return (
    <div className="csv-container">
      <h3>Upload File CSV</h3>
      <input type="file" accept=".csv" onChange={onFileUpload} />
      {csvData.length > 0 && (
        <div className="csv-table-wrapper">
          <table className="csv-table">
            <thead>
              <tr>
                {csvData[0].map((header, index) => (
                  <th key={index}>{header}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {currentTableData().map((row, rowIndex) => (
                <tr key={rowIndex}>
                  {row.map((cell, cellIndex) => (
                    <td key={cellIndex}>{cell}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
          <div className="pagination">
            <button
              onClick={() => paginate(currentPage - 1)}
              disabled={currentPage === 1}
            >
              Previous
            </button>
            {getPaginationButtons(currentPage, totalPages).map((page, index) => (
              <button
                key={index}
                className={currentPage === page ? 'active' : ''}
                onClick={() => {
                  if (page !== '...') paginate(page);
                }}
                disabled={page === '...'}
              >
                {page}
              </button>
            ))}
            <button
              onClick={() => paginate(currentPage + 1)}
              disabled={currentPage === totalPages}
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

// PropTypes validation
CSVContainer.propTypes = {
  csvData: PropTypes.arrayOf(PropTypes.array).isRequired, // Ensure csvData is an array of arrays
  onFileUpload: PropTypes.func.isRequired,              // Ensure onFileUpload is a function
  rowsPerPage: PropTypes.number.isRequired,             // Ensure rowsPerPage is a number
};

export default CSVContainer;

