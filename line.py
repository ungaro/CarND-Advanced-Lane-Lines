import numpy as np

class Line:
    def __init__(self):
        # if the first frame of video has been processed
        self.first_frame_processed = False  
        
        self.img = None
        
        self.mse_tolerance = 0.01
        self.left_fit = [np.array([False])] 
        self.right_fit = [np.array([False])] 
        
        self.y_eval = 700
        self.midx = 640
        self.ym_per_pix = 30/720 # meters per pixel in y dimension
        self.xm_per_pix = 3.7/880 # meters per pixel in x dimension
        self.curvature = None
        
        self.n = 15
        # x values of the last n fits of the line
        self.recent_xfitted = [] 
        #average x values of the fitted line over the last n iterations
        self.bestx = None     
        #polynomial coefficients averaged over the last n iterations
        self.best_fit = None  
        #polynomial coefficients for the most recent fit
        self.current_fit = [np.array([False])]  
 





       
    def update_fits(self, left_fit, right_fit):
        """Update the co-efficients of fitting polynomial
        """
    
        if self.first_frame_processed:
            left_error = ((self.left_fit[0] - left_fit[0]) ** 2).mean(axis=None)      
            right_error = ((self.right_fit[0] - right_fit[0]) ** 2).mean(axis=None)        
            if left_error < self.mse_tolerance:
                self.left_fit = 0.75 * self.left_fit + 0.25 * left_fit   
            if right_error < self.mse_tolerance:
                self.right_fit = 0.75 * self.right_fit + 0.25 * right_fit
        else:
            self.right_fit = right_fit
            self.left_fit = left_fit
      

        self.update_curvature(self.left_fit)
     
 
    def update_curvature(self, fit):
        ploty = np.linspace(0, 719, 720 )
        fitx = fit[0]*ploty**2 + fit[1]*ploty + fit[2]

        if(len(self.recent_xfitted) > self.n):
            self.recent_xfitted.pop(0)

        self.recent_xfitted.append(fitx)
        self.bestx = np.mean(self.recent_xfitted,axis=0)
        self.best_fit = np.polyfit(ploty, self.bestx, 2)
        self.current_fit = fit


        line_fit=self.best_fit

        #bottom of image, ie where the car is 
        y_eval = np.max(ploty)

        plotx = line_fit[0]*ploty**2 + line_fit[1]*ploty + line_fit[2]

        fit_world = np.polyfit(ploty*self.ym_per_pix, plotx*self.xm_per_pix, 2)
        
        curvature = ((1 + (2*fit_world[0]*y_eval*self.ym_per_pix + fit_world[1])**2)**1.5) / np.absolute(2*fit_world[0])
        self.curvature = curvature
        #print("Curvature: ",curvature)

    def get_position_from_center(self):
        x_left_pix = self.left_fit[0]*(self.y_eval**2) + self.left_fit[1]*self.y_eval + self.left_fit[2]
        x_right_pix = self.right_fit[0]*(self.y_eval**2) + self.right_fit[1]*self.y_eval + self.right_fit[2]
        
        return ((x_left_pix + x_right_pix)/2.0 - self.midx) * self.xm_per_pix
            
        