#include <boost/shared_ptr.hpp> 
#include <opencv2/opencv.hpp>

cv::Scalar FINAL_LINE_COLOR (255, 255, 255);
cv::Scalar WORKING_LINE_COLOR(127, 127, 127);

class PolygonDrawer {
public:

  std::string window_name_;
  bool done_;
  cv::Point current_;
  std::vector<cv::Point> points_;
  boost::shared_ptr<cv::Mat> imgPtr;

  PolygonDrawer(const std::string window_name, std::string imgName){
    window_name_ = window_name;
    done_ = false;
    current_ = cv::Point(0, 0); // Current position, so we can draw the line-in-progress
    imgPtr.reset(new cv::Mat(cv::imread(imgName)));
  }

  static void onMouse( int event, int x, int y, int f, void* data ) {
    PolygonDrawer *curobj = reinterpret_cast<PolygonDrawer*>(data);
    if (curobj->done_) // Nothing more to do
      return;

    if(event == cv::EVENT_MOUSEMOVE)
      // We want to be able to draw the line-in-progress, so update current mouse position
      curobj->current_ = cv::Point(x, y);
    else if(event == cv::EVENT_LBUTTONDOWN) {
      // Left click means adding a point at current position to the list of points
      printf("Adding point #%zu with position(%d,%d) \n", curobj->points_.size(), x, y);
      curobj->points_.push_back(cv::Point(x, y));
    } else if(event == cv::EVENT_RBUTTONDOWN) {
      // Right click means we're done
      printf("Completing polygon with %zu points \n", curobj->points_.size());
      curobj->done_ = true;
    }
  }

  void run() {
    // Let's create our working window and set a mouse callback to handle events
    cv::namedWindow(window_name_, cv::WINDOW_KEEPRATIO);
    cv::imshow(window_name_, *imgPtr);
    cv::waitKey(1);
    cv::setMouseCallback(window_name_, onMouse, this);
    while(!done_) {
      cv::Mat img;
      imgPtr->copyTo(img);
      if (points_.size() > 0){
        // Draw all the current polygon segments
        const cv::Point *pts = (const cv::Point*) cv::Mat(points_).data;
        int npts = cv::Mat(points_).rows;

        cv::polylines(img, &pts, &npts, 1, false, FINAL_LINE_COLOR);
        // And  also show what the current segment would look like
        cv::line(img, points_[points_.size()-1], current_, WORKING_LINE_COLOR, 1.0);
        // Update the window
      }
      cv::imshow(window_name_, img);
      // And wait 50ms before next iteration (this will pump window messages meanwhile)
      if(cv::waitKey(50) == 27)
        done_ = true;
    }
    const cv::Point *pts = (const cv::Point*) cv::Mat(points_).data;
    int npts = cv::Mat(points_).rows;

    // user finished entering the polygon points
    if (points_.size() > 0) {
      cv::fillPoly(*imgPtr, &pts, &npts, 1, FINAL_LINE_COLOR);
      cv::imshow(window_name_, *imgPtr);
      //Waiting for the user to press any key
      cv::waitKey();
      cv::destroyWindow(window_name_);
    }
  }
};


int main(int argc, char** argv) {
  PolygonDrawer pd("Polygon", argv[1]);
  pd.run();
  // cv2.imwrite("polygon.png", image)
  // print("Polygon = %s" % pd.points)
}