import React, { useState, useEffect } from 'react';
import { Container, Table, Button, Badge } from 'react-bootstrap';
import CourseModal from './CoursesModal';
import Papa from 'papaparse';
import CourseOfferingsModal from './CourseOfferingModal';

const CoursesPage = () => {
  const [courses, setCourses] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [selectedCourse, setSelectedCourse] = useState(null);
  const [error, setError] = useState(null);
  const [showOfferingsModal, setShowOfferingsModal] = useState(false);
  const [selectedCourseId, setSelectedCourseId] = useState(null);
  const fetchCourses = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/api/courses/');
      const data = await response.json();
      setCourses(data);
    } catch (error) {
      setError('Error fetching courses');
    }
  };

  useEffect(() => {
    fetchCourses();
  }, []);

  const handleDelete = async (courseId) => {
    if (window.confirm(`Are you sure you want to delete course ${courseId}?`)) {
      try {
        const response = await fetch(`http://127.0.0.1:5000/api/courses/${courseId}`, {
          method: 'DELETE'
        });
        if (response.ok) {
          fetchCourses();
          alert('Course deleted successfully');
        } else {
          const errorData = await response.json();
          throw new Error(errorData.error || 'Failed to delete course');
        }
      } catch (error) {
        setError(`Error deleting course: ${error.message}`);
        alert(`Error deleting course: ${error.message}`);
      }
    }
  };
  

  const handleEdit = (course) => {
    setSelectedCourse(course);
    setShowModal(true);
  };

  return (
    <Container className="py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>Courses</h1>
        <Button variant="primary" onClick={() => setShowModal(true)}>
          Add Course
        </Button>
      </div>

      <Table striped bordered hover responsive>
        <thead>
          <tr>
            <th>Course ID</th>
            <th>Course Name</th>
            <th>Credits</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {courses.map((course) => (
            <tr key={course.course_id}>
              <td>{course.course_id}</td>
              <td>{course.course_name}</td>
              <td>{course.credits}</td>
              <td>
                <Button 
                  variant="primary" 
                  size="sm" 
                  className="me-2"
                  onClick={() => handleEdit(course)}
                >
                  Edit
                </Button>
                <Button
        variant="info"
        size="sm"
        className="me-2"
        onClick={() => {
            setSelectedCourseId(course.course_id);
            setShowOfferingsModal(true);
        }}
    >
        Offerings
    </Button>
                <Button 
                  variant="danger" 
                  size="sm"
                  onClick={() => {
                    handleDelete(course.course_id);
                  }}
                >
                  Delete
                </Button>
              </td>
            </tr>
          ))}
        </tbody>
      </Table>

      <CourseModal 
        show={showModal}
        onHide={() => {
          setShowModal(false);
          setSelectedCourse(null);
        }}
        course={selectedCourse}
        onSave={fetchCourses}
      />



<CourseOfferingsModal
    show={showOfferingsModal}
    onHide={() => setShowOfferingsModal(false)}
    courseId={selectedCourseId}
/>
    </Container>
  );
};

export default CoursesPage;
