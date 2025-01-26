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
  const [containerWidth, setContainerWidth] = useState(600); // Chiều rộng mặc định
  const totalPages = Math.ceil((csvData.length - 1) / rowsPerPage);

  const paginate = (pageNumber) => {
    if (pageNumber >= 1 && pageNumber <= totalPages) {
      setCurrentPage(pageNumber);
    }
  };

  const currentTableData = () => {
    const startIndex = (currentPage - 1) * rowsPerPage + 1;
    const endIndex = startIndex + rowsPerPage;
    return csvData.slice(startIndex, endIndex);
  };

  // Xử lý kéo để thay đổi kích thước
  const handleMouseDown = (e) => {
    e.preventDefault();
    const startX = e.clientX;

    const handleMouseMove = (moveEvent) => {
      const delta = moveEvent.clientX - startX;
      setContainerWidth((prevWidth) => Math.max(300, prevWidth + delta)); // Chiều rộng tối thiểu là 300px
    };

    const handleMouseUp = () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };

    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseup', handleMouseUp);
  };

  return (
    <div
      className="csv-container"
      style={{ width: `${containerWidth}px` }}
    >
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
      {/* Thanh kéo để thay đổi kích thước */}
      <div
        className="resize-handle"
        onMouseDown={handleMouseDown}
      />
    </div>
  );
}

// PropTypes validation
CSVContainer.propTypes = {
  csvData: PropTypes.arrayOf(PropTypes.array).isRequired,
  onFileUpload: PropTypes.func.isRequired,
  rowsPerPage: PropTypes.number.isRequired,
};

export default CSVContainer;