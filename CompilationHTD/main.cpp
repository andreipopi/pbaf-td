#include <htd/main.hpp>
#include <htd_io/main.hpp>
#include <htd_cli/main.hpp>

#include <csignal>
#include <memory>
#include <chrono>
#include <sstream>


//Create a management instance of the 'htd' library in order to allow centralized configuration.
//std::unique_ptr<htd::LibraryInstance> manager(htd::createManagementInstance(htd::Id::FIRST));
htd::LibraryInstance * manager = htd :: createManagementInstance (1);

/**
 *  Sample fitness function which minimizes width and height of the decomposition.
 *
 *  Width is of higher priority than height, i.e., at first, the width is minimized
 *  and if two decompositions have the same width, the one of lower height is chosen.
 */
class FitnessFunction : public htd::ITreeDecompositionFitnessFunction
{
    public:
        FitnessFunction(void)
        {

        }

        ~FitnessFunction()
        {

        }

        htd::FitnessEvaluation * fitness(const htd::IMultiHypergraph & graph,
                                         const htd::ITreeDecomposition & decomposition) const
        {
            HTD_UNUSED(graph)

            /**
              * Here we specify the fitness evaluation for a given decomposition.
              * In this case, we select the maximum bag size and the height.
              */
            return new htd::FitnessEvaluation(2,
                                              -(double)(decomposition.maximumBagSize()),
                                              -(double)(decomposition.height()));
        }

        FitnessFunction * clone(void) const
        {
            return new FitnessFunction();
        }
};

/**
 * Signal handling procedure.
 */
void handleSignal(int signal)
{
    switch (signal)
    {
        case SIGINT:
        case SIGTERM:
        {
            manager->terminate();

            break;
        }
        default:
        {
            break;
        }
    }

    std::signal(signal, handleSignal);
}

int main(int, const char * const * const)
{
    std::signal(SIGINT, handleSignal);
    std::signal(SIGTERM, handleSignal);

    std::srand(0);

    htd_io::GrFormatImporter importer(manager);
    htd::IMultiGraph * graph = importer.import(std::cin);

    //htd_io::LpFormatImporter importer(manager);
    //htd_io::HgrFormatImporter importer(manager);
    //htd::IDirectedMultiGraph * graph = importer.import(std::cin);

    //htd_io::HgrFormatImporter importer(manager);
    //htd::NamedMultiHypergraph<std::string, std::string> * graph = importer.import(std::cin);
    
    // Create an instance of the fitness function.
    FitnessFunction fitnessFunction;

    /**
     *  This operation changes the root of a given decomposition so that the provided
     *  fitness function is maximized. When no fitness function is provided to the
     *  constructor, the constructed optimization operation does not perform any
     *  optimization and only applies provided manipulations.
     */
    htd::TreeDecompositionOptimizationOperation * operation =
        new htd::TreeDecompositionOptimizationOperation(manager, fitnessFunction.clone());

    /**
     *  Set the previously created management instance to support graceful termination.
     */
    operation->setManagementInstance(manager);

    /**
     *  Set the vertex selections strategy (default = exhaustive).
     *
     *  In this case, we want to select (at most) 10 vertices of the input decomposition randomly.
     */
    operation->setVertexSelectionStrategy(new htd::RandomVertexSelectionStrategy(10));

    /**
     *  Set desired manipulations. In this case we want a nice (= normalized) tree decomposition.
     */
    operation->addManipulationOperation(new htd::NormalizationOperation(manager));

    operation->addManipulationOperation(new htd::AddEmptyLeavesOperation(manager));

    operation->addManipulationOperation(new htd::AddEmptyRootOperation(manager));
    operation->addManipulationOperation(new htd::InducedSubgraphLabelingOperation(manager));
    operation->addManipulationOperation(new htd::LimitMaximumIntroducedVertexCountOperation(manager,1,false));
    operation->addManipulationOperation(new htd::LimitMaximumForgottenVertexCountOperation(manager,1));

    /**
     *  Optionally, we can set the vertex elimination algorithm.
     *  We decide to use the min-degree heuristic in this case.
     */
    manager->orderingAlgorithmFactory()
        .setConstructionTemplate(new htd::MinDegreeOrderingAlgorithm(manager));

    // Get the default tree decomposition algorithm. One can also choose a custom one.
    htd::ITreeDecompositionAlgorithm * baseAlgorithm =
        manager->treeDecompositionAlgorithmFactory().createInstance();

    /**
     *  Set the optimization operation as manipulation operation in order
     *  to choose the optimal root reducing height of the tree decomposition.
     */
    baseAlgorithm->addManipulationOperation(operation);

    /**
     *  Create a new instance of htd::IterativeImprovementTreeDecompositionAlgorithm based
     *  on the base algorithm and the fitness function. Note that the fitness function can
     *  be an arbiraty one and can differ from the one used in the optimization operation.
     */
    htd::IterativeImprovementTreeDecompositionAlgorithm algorithm(manager,
                                                                  baseAlgorithm,
                                                                  fitnessFunction.clone());

    /**
     *  Set the maximum number of iterations after which the best decomposition with
     *  respect to the fitness function shall be returned. Use value 1 to make the
     *  iterative algorithm return the first decomposition found.
     */
    algorithm.setIterationCount(10);

    /**
     *  Set the maximum number of iterations without improvement after which the algorithm returns
     *  best decomposition with respect to the fitness function found so far. A limit of 0 aborts
     *  the algorithm after the first non-improving solution has been found, i.e. the algorithm
     *  will perform a simple hill-climbing approach.
     */
    algorithm.setNonImprovementLimit(3);

    // Record the optimal maximal bag size of the tree decomposition to allow printing the progress.
    std::size_t optimalBagSize = (std::size_t)-1;

    /**
     *  Compute the decomposition. Note that the additional, optional parameter of the function
     *  computeDecomposition() in case of htd::IterativeImprovementTreeDecompositionAlgorithm
     *  can be used to intercept every new decomposition. In this case we output some
     *  intermediate information upon perceiving an improved decompostion.
     */
    htd::ITreeDecomposition * decomposition =
        algorithm.computeDecomposition(*graph, [&](const htd::IMultiHypergraph & graph,
                                                   const htd::ITreeDecomposition & decomposition,
                                                   const htd::FitnessEvaluation & fitness)
    {
        // Disable warnings concerning unused variables.
        HTD_UNUSED(graph)
        HTD_UNUSED(decomposition)

        std::size_t bagSize = -fitness.at(0);

        /**
         *  After each improvement we print the current optimal
         *  width + 1 and the time when the decomposition was found.
         */
        if (bagSize < optimalBagSize)
        {
            optimalBagSize = bagSize;

            std::chrono::milliseconds::rep msSinceEpoch =
                std::chrono::duration_cast<std::chrono::milliseconds>
                        (std::chrono::system_clock::now().time_since_epoch()).count();

            std::cout << "c status " << optimalBagSize << " " << msSinceEpoch << std::endl;
        }
    });

    // If a decomposition was found we want to print it to stdout.
    if (decomposition != nullptr)
    {
        /**
         *  Check whether the algorithm indeed computed a valid decomposition.
         *
         *  algorithm.isSafelyInterruptible() for decomposition algorithms allows to
         *  find out if the algorithm is safely interruptible. If the getter returns
         *  true, the algorithm guarantees that the computed decomposition is indeed
         *  a valid one and that all manipulations and all labelings were applied
         *  successfully.
         */
        if (!manager->isTerminated() || algorithm.isSafelyInterruptible())
        {
            // Print the height of the decomposition to stdout.
            std::cout << decomposition->height() << std::endl;
            
            // Print the size of the largest bag of the decomposition to stdout.
            std::cout << decomposition->maximumBagSize() << std::endl;
            
            std::cout << "Human Tree Decomposition" << std::endl;
            // Print the whole decomposition using htd_io::HumanReadableExporter.
            htd_io::HumanReadableExporter exporter;
            exporter.write(*decomposition, *graph, std::cout);

            //std::cout << "Machine Tree Decomposition" << std::endl;
            // Print the whole decomposition using htd_io::HumanReadableExporter.
            //htd_io::TdFormatExporter exporter2;
            //exporter2.write(*decomposition, *graph, std::cout);
            
            std::cout << "Traversal" <<std::endl;
        }

    

        htd::PostOrderTreeTraversal traversal;
        traversal.traverse(*decomposition, [&] (htd::vertex_t vertex,
                                                htd::vertex_t parent,
                                                std::size_t distanceToRoot)
        {
            //for (htd::index_t index =0; index< distanceToRoot; ++index){
            //    std::cout << " ";
            //}


            
            std::cout << vertex << " " ;

            std::vector<htd::vertex_t> bagelems = decomposition->bagContent(vertex);
            size_t numverteces = bagelems.size();
                size_t i = 0;
                std::ostringstream bagel;
                bagel << "[";
                for (const auto& v : bagelems) {
                    bagel << v; // Convert to string and append without space
                    if (++i < numverteces) {
                        bagel << ",";
                    }
                }
                bagel << "]";
                std::cout << bagel.str();

            if(decomposition->isIntroduceNode(vertex)){
                std::cout << " intro";
            }
            else if(decomposition->isForgetNode(vertex)){
                std::cout << " rem";
            }
            else if(decomposition->isJoinNode(vertex)){
                std::cout << " join";
            }
            else{
                std::cout << " leaf";
            }

            //doesn't worki like this: apparently not meant to get access to children 
            //std::vector<htd::vertex_t> childBagsUnion;
            //decomposition->getChildBagSetUnion(vertex, childBagsUnion);
            //std::cout << "children " << childBagsUnion;

        
            std::vector<htd::vertex_t> introducedVertices;
            // Loop over each vertex in the node
            for (htd::vertex_t v : decomposition->bagContent(vertex)) {
            // Check if the vertex is introduced
                if (decomposition->isIntroducedVertex(vertex, v)) {
                    // If it is, add it to the list
                    introducedVertices.push_back(v);
                }
            }
            std::vector<htd::vertex_t> removedVertices;
            // htd somehow keeps track of forgotten vertices
            for (htd::vertex_t v : decomposition->forgottenVertices(vertex)) {
            // Check if the vertex is forgotten
                if (decomposition->isForgottenVertex(vertex, v)) {
                    // If it is, add it to the list
                    removedVertices.push_back(v);
                }
            }

            if(decomposition->isIntroduceNode(vertex)){
                //std::cout << " introduced ";

                size_t numIntr = introducedVertices.size();
                size_t c = 0;
                std::ostringstream intr;
                intr << " [";
                for (const auto& v : introducedVertices) {
                    intr << v; // Convert to string and append without space
                    if (++c < numIntr) {
                        intr << ",";
                    }
                }
                intr << "]";
                std::cout << intr.str();
            }
            else if(decomposition->isForgetNode(vertex)){
                //std::cout << " removed ";

                size_t numRem = removedVertices.size();
                size_t c = 0;
                std::ostringstream rem;
                rem << " [";
                for (const auto& v : removedVertices) {
                    rem << v; // Convert to string and append without space
                    if (++c < numRem) {
                        rem << ",";
                    }
                }
                rem << "]";
                std::cout << rem.str();
            }

            
            auto &edges = decomposition->inducedHyperedges(vertex);
            size_t numEdges = edges.size();
            size_t count = 0;
            
            
            std::cout << " edges ";
            std::cout << "[";
            for (const htd::Hyperedge & e: decomposition->inducedHyperedges(vertex)){
                    //for(htd::index_t index = 0; index < distanceToRoot+1; ++index){
                    //    std::cout << " ";
                    //}
                size_t count2 = 0;
                std::ostringstream result;
                size_t numElemsInEdge = e.elements().size();
                result << "[";
                for (const auto& elem : e.elements()) {
                    result << elem; // Convert to string and append without space
                    if (++count2 < numElemsInEdge) {
                        result << ",";
                    }
                }
                result << "]";
                std::cout << result.str();

                if (++count < numEdges) {
                    std::cout << ",";
                }
            }

            std::cout << "]"; // need to make it a list of lists for python parsing
            
            
        
            std::cout << " " << parent;
            std::cout << std::endl;

        });

        delete decomposition;
    }

    delete graph;

    return 0;
}