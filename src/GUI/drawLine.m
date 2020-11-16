function [ outGry ] = drawLine( inGry, p0, p1, pnSize, val )
% function for drawing lines for UI
outGry = inGry;

p0 = double(p0);
p1 = double(p1);

% difference in absolute row and columns
difRow = abs( p0(1) - p1(1) );
difCol = abs( p0(2) - p1(2) );

rowRange = [1 size(inGry,1)];
colRange = [1 size(inGry,2)];
% check if either calue is 0
if( difRow == 0 || difCol == 0 )
    row0 = intorange( min([p0(1) p1(1)]) - pnSize, rowRange );
    row1 = intorange( max([p0(1) p1(1)]) + pnSize, rowRange );
   
    col0 = intorange( min([p0(2) p1(2)]) - pnSize, colRange );
    col1 = intorange( max([p0(2) p1(2)]) + pnSize, colRange );
      
    outGry( round(row0):round(row1), round(col0):round(col1) ) = val;
else    
    if( difRow > difCol )
        if( p0(1) > p1(1) )
            tmp = p0;
            p0 = p1;
            p1 = tmp;
        end
    
        A = ( p1(2) - p0(2) ) / ( p1(1) - p0(1));
        
        rr0 = intorange( p0(1), rowRange );
        rr1 = intorange( p1(1), rowRange );
        for row = rr0:rr1
            col = round( A * ( row - p0(1) ) + p0(2) );
            col0 = intorange( col - pnSize, colRange );
            col1 = intorange( col + pnSize, colRange );
            row0 = intorange( row - pnSize, rowRange );
            row1 = intorange( row + pnSize, rowRange );            
            outGry( round(row0):round(row1), round(col0):round(col1) ) = val;
        end        
    else
        if( p0(2) > p1(2) )
            tmp = p0;
            p0 = p1;
            p1 = tmp;
        end
        A = ( p1(1) - p0(1) ) / ( p1(2) - p0(2) );
        
        cc0 = intorange( p0(2), colRange );
        cc1 = intorange( p1(2), colRange );
        for col = cc0:cc1
            row = round( A * ( col - p0(2) ) + p0(1) );
            row0 = intorange( row - pnSize, rowRange );
            row1 = intorange( row + pnSize, rowRange );
            col0 = intorange( col - pnSize, colRange );
            col1 = intorange( col + pnSize, colRange );
            outGry( round(row0):round(row1), round(col0):round(col1) ) = val;
        end                
   end
end

end

function dst = intorange( src, range )
%check range given src image
dst = src;
if( dst < range(1) )
    dst = range(1);
end
if( dst > range(2) )
    dst = range(2);
end

end
